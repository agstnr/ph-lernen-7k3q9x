# PH Lernen

Static GitHub Pages app. The current expansion is a **draft**, not a claim of exhaustive subject coverage.

## Learning changes

- All 4,127 questions use answer choices. The 171 former recall cards retain their IDs, original answers and source references; their changed choice versions are marked as drafts.
- Multiple choice supports selecting and deselecting answers, explicit submission, and exact-set grading. Selecting only some correct options is incorrect.
- 3,867 automatically generated single-choice cloze questions supplement the existing questions. They test the **original wording** of text passages, not necessarily understanding or application. They are not individually reviewed. Distractors for converted cards are other answers from the same course and need editorial review.
- All 1,830 pages of the 31 original PDFs have WebP page images restored from SHA-256-verified originals. Existing question sources display these pages. Cloze questions offer the source page as an optional hint and expand it after submission so the page does not immediately reveal the answer.
- “Alle Fragen dieser Auswahl durchgehen” includes every active question in the current filter, including already learned questions, independently of the daily new-card limit.
- “Folienabdeckung ansehen” lists pages without a question reference and pages flagged as visually rich. A reference alone does **not** demonstrate full content coverage.

## Remaining work before claiming full coverage

`data/abdeckung.json` tracks 1,824 pages of learning material/source documents. Of these, 462 have no new generated text question. Some already have existing questions; others are title, reference or diagram pages. Each needs classification. Every visual learning objective must be checked against the restored page image and given a meaningful choice question where relevant. Text questions also need semantic review for omissions, suitable distractors, and factual accuracy. Neither the question count nor the presence of a question on a page proves that every learning objective has been covered.

The six pages of literature lists, the spreadsheet and the original exam-question documents are not expanded automatically. Existing questions remain available.

## Validation

```sh
node --test tests/choice.test.cjs
python tests/data.test.py
```

Browser flow checks (requires Playwright and Chromium, serve the repo under `/ph-lernen-7k3q9x/`):

```sh
PH_TEST_URL=http://localhost:8765/ph-lernen-7k3q9x/ node tests/browser.cjs
```

`python scripts/expand_questions.py` regenerates cloze drafts and the coverage manifest deterministically from the repository's page text. It does not infer diagram meaning. `scripts/restore_slides.py` accepts a local JSON download manifest and verifies the source PDF hashes before rendering. No account credentials, signed download links or private Drive IDs are needed in the repository.
