(function (global) {
  'use strict';
  const multiple = (q) => q.optionen.filter((o) => o.richtig).length > 1;
  const correct = (q, selected) => q.optionen.every((o, i) => !!o.richtig === selected.has(i));
  global.Choice = { multiple, correct };
  if (typeof module !== 'undefined') module.exports = global.Choice;
})(typeof window !== 'undefined' ? window : globalThis);
