/*
 * Wiederholungsplanung nach FSRS-6 (Free Spaced Repetition Scheduler).
 *
 * Die Formeln und Standardparameter sind aus ts-fsrs 6.0.0 übertragen
 * (src/models/fsrs-6/algorithm.ts und constants.ts, https://github.com/open-spaced-repetition/ts-fsrs).
 * Übernommen sind nur die Rechenschritte für Stabilität, Schwierigkeit, Abrufwahrscheinlichkeit und Intervall.
 * Vereinfacht gegenüber ts-fsrs: keine Lernschritte in Minuten. „Nochmal“ legt die Karte für 10 Minuten zurück,
 * sonst wird in ganzen Tagen geplant. Kein Zufallsaufschlag (fuzz), keine persönliche Parameteroptimierung.
 *
 * ts-fsrs steht unter MIT-Lizenz:
 *   MIT License
 *   Copyright (c) 2026 Open Spaced Repetition
 *   Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
 *   documentation files (the "Software"), to deal in the Software without restriction, including without limitation
 *   the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
 *   to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 *   The above copyright notice and this permission notice shall be included in all copies or substantial portions
 *   of the Software.
 *   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
 *   THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 *   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
 *   CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 *   DEALINGS IN THE SOFTWARE.
 */
"use strict";
(function (global) {
  // Standardgewichte FSRS-6 (ts-fsrs 6.0.0, FSRS6_DEFAULT_WEIGHTS)
  const W = [0.212, 1.2931, 2.3065, 8.2956, 6.4133, 0.8334, 3.0194, 0.001, 1.8722, 0.1666, 0.796,
    1.4835, 0.0614, 0.2629, 1.6483, 0.6014, 1.8729, 0.5425, 0.0912, 0.0658, 0.1542];
  const S_MIN = 0.001, S_MAX = 36500;
  const ZIEL_ABRUF = 0.9; // gewünschte Abrufwahrscheinlichkeit zum Fälligkeitszeitpunkt (Standard in ts-fsrs)
  const NOCHMAL_MINUTEN = 10;
  const runde = (x) => Math.round(x * 1e8) / 1e8;
  const begrenze = (x, a, b) => Math.min(Math.max(x, a), b);
  const DECAY = -W[20];
  const FAKTOR = runde(Math.exp(Math.log(0.9) / DECAY) - 1);

  /** Abrufwahrscheinlichkeit nach t Tagen bei Stabilität s */
  const abrufbarkeit = (t, s) => runde(Math.pow(1 + (FAKTOR * t) / s, DECAY));
  const startStabilitaet = (g) => begrenze(W[g - 1], S_MIN, S_MAX);
  const startSchwierigkeit = (g) => runde(W[4] - Math.exp((g - 1) * W[5]) + 1);
  function naechsteSchwierigkeit(d, g) {
    const delta = -W[6] * (g - 3);
    const neu = d + runde((delta * (10 - d)) / 9);
    return begrenze(runde(W[7] * startSchwierigkeit(4) + (1 - W[7]) * neu), 1, 10);
  }
  function stabilitaetNachErfolg(d, s, r, g) {
    const hart = g === 2 ? W[15] : 1, leicht = g === 4 ? W[16] : 1;
    return runde(begrenze(s * (1 + Math.exp(W[8]) * (11 - d) * Math.pow(s, -W[9]) * (Math.exp((1 - r) * W[10]) - 1) * hart * leicht), S_MIN, S_MAX));
  }
  function stabilitaetNachVergessen(d, s, r) {
    return runde(begrenze(W[11] * Math.pow(d, -W[12]) * (Math.pow(s + 1, W[13]) - 1) * Math.exp((1 - r) * W[14]), S_MIN, S_MAX));
  }
  function stabilitaetKurzfristig(s, g) {
    const f = Math.pow(s, -W[19]) * Math.exp(W[17] * (g - 3 + W[18]));
    return runde(begrenze(s * (g >= 2 ? Math.max(f, 1) : f), S_MIN, S_MAX));
  }

  /** Ein Schritt des Gedächtnismodells. zustand {s, d} oder null für eine neue Karte, t = Tage seit der letzten Wiederholung, g = 1..4 */
  function schritt(zustand, t, g) {
    if (!zustand) return { d: begrenze(startSchwierigkeit(g), 1, 10), s: startStabilitaet(g) };
    const { d, s } = zustand;
    const r = abrufbarkeit(t, s);
    let neuS;
    if (t === 0) neuS = stabilitaetKurzfristig(s, g);
    else if (g === 1) neuS = begrenze(runde(s / Math.exp(W[17] * W[18])), S_MIN, stabilitaetNachVergessen(d, s, r));
    else neuS = stabilitaetNachErfolg(d, s, r, g);
    return { d: naechsteSchwierigkeit(d, g), s: neuS };
  }

  /** Intervall in Tagen, nach dem die Abrufwahrscheinlichkeit auf ZIEL_ABRUF gesunken ist */
  const intervall = (s) => Math.max(Math.round((s / FAKTOR) * (Math.pow(ZIEL_ABRUF, 1 / DECAY) - 1)), 1);

  const tagesbeginn = (d) => { const x = new Date(d); x.setHours(0, 0, 0, 0); return x; };
  const tageZwischen = (a, b) => Math.max(0, Math.round((tagesbeginn(b) - tagesbeginn(a)) / 86400000));

  /**
   * Bewertet eine Karte. karte: gespeicherter Stand {s, d, letzte, faellig, wdh, fehler, verlauf} oder undefined.
   * note: 1 Nochmal, 2 Schwer, 3 Gut, 4 Leicht. Gibt den neuen Stand zurück (verändert die Eingabe nicht).
   */
  function bewerte(karte, note, jetzt = new Date()) {
    const t = karte?.letzte ? tageZwischen(new Date(karte.letzte), jetzt) : 0;
    const neu = schritt(karte?.s ? { s: karte.s, d: karte.d } : null, t, note);
    const faellig = note === 1 ? new Date(jetzt.getTime() + NOCHMAL_MINUTEN * 60000)
      : new Date(tagesbeginn(jetzt).getTime() + intervall(neu.s) * 86400000);
    return {
      s: neu.s, d: neu.d, letzte: jetzt.toISOString(), faellig: faellig.toISOString(),
      wdh: (karte?.wdh || 0) + 1, fehler: (karte?.fehler || 0) + (note === 1 ? 1 : 0),
      verlauf: [...(karte?.verlauf || []), { am: jetzt.toISOString(), note }],
    };
  }

  /** Vorschau: in wie vielen Tagen die Karte bei jeder Note wieder käme (0 = in 10 Minuten) */
  function vorschau(karte, jetzt = new Date()) {
    const o = {};
    for (const g of [1, 2, 3, 4]) { const k = bewerte(karte, g, jetzt); o[g] = g === 1 ? 0 : tageZwischen(jetzt, new Date(k.faellig)); }
    return o;
  }

  /** Aktuelle Abrufwahrscheinlichkeit einer gelernten Karte */
  const aktuelleAbrufbarkeit = (karte, jetzt = new Date()) => karte?.s ? abrufbarkeit(tageZwischen(new Date(karte.letzte), jetzt), karte.s) : null;

  global.FSRS = { bewerte, vorschau, aktuelleAbrufbarkeit, intervall, schritt, abrufbarkeit, ZIEL_ABRUF };
  if (typeof module !== "undefined") module.exports = global.FSRS;
})(typeof window !== "undefined" ? window : globalThis);
