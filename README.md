# Repository for Paper in Review: Legislating in Parallel: Explaining Performance Differences Beyond Control Flow in Cross-Organizational Process Mining

This repository provides all implementations and data collected and generated to perform cross-organizational process mining on the legislation processes of three German state parliaments — Baden-Württemberg, Berlin, and Brandenburg — which legislate similar matters in parallel under distinct jurisdictions, as published by their documentation services (Parlamentsdokumentation). The analysis follows a two-phase design:

1. A **baseline analysis** relying solely on control-flow information from the event logs (cycle times, process variants, dotted charts, and rule induction to surface delay patterns) — `BaselineAnalysis/`.
2. An **enrichment analysis** that lifts this restriction by adding political context features, distinguishing _in-data features_ (derived from the event logs themselves, e.g. draft authorship, topic classification, legislative workload) from _out-of-data features_ (drawn from external sources, e.g. parliamentary composition, party alignment, and Wahl-O-Mat-based agreement scores) — `AdvancedAnalysis/`. These features are evaluated both individually and in a delay-classification task to assess whether context can explain performance differences that control-flow alone cannot.

Note that some of the documentation services provide new raw data on a daily basis; the code in this repository can be used to regenerate event logs from newer raw data as it becomes available.

## Repository Structure

- `OriginalData/` – Raw XML exports as obtained from the documentation services of the three parliaments, one subfolder per state.
- `EventLogGenerators/` – Notebooks to generate `.xes` event logs from `OriginalData/`, either covering all process types or a single selected type.
- `all-data-xes/` – Generated event logs in `.xes` format (git-ignored; regenerate via `EventLogGenerators/`, or restore from `EventLogs/`). These logs cover all process types and are filtered down for specific analyses further along the pipeline.
- `EventLogs/` – Zipped copies of the `all-data-xes/` event logs, for direct download without having to rerun the generators; regenerate them via `EventLogGenerators/` instead.
- `BaselineAnalysis/` – Baseline cross-organizational process mining analysis (performance measures, process type exploration).
  - `LawmakingAnalysis/` – Baseline analysis specifically about cycle-time differences and outcome/rule induction for lawmaking traces.
- `AdvancedAnalysis/` – Generation of in-data and out-of-data political context features (including Wahl-O-Mat agreement scores and topic embeddings) and the subsequent enrichment/classification analyses. See [AdvancedAnalysis pipeline](#advancedanalysis-pipeline) below.
- `requirements.txt` – Python dependencies.
- `license` – Licensing terms for code and data in this repository.

## Requirements

See `requirements.txt`. The code was run with Python 3.13; Python 2 compatibility is not guaranteed.

This repository uses [Git LFS](https://git-lfs.com/) to store the large `.zip` files under `EventLogs/` and `AdvancedAnalysis/data-csv/`. Please install Git LFS (`git lfs install`) **before** cloning, then clone as usual — Git LFS will transparently download the actual file contents in place of pointer files. If you already cloned without Git LFS installed, install it and run `git lfs pull` from within the repository to fetch the real files. Individual files can also be downloaded directly from GitHub's web UI by opening the file and clicking "Download raw file", without needing Git LFS locally.

## Usage / Reproducing Results

The baseline and the enrichment analysis share intermediate event logs: the lawmaking part of the baseline analysis (steps 6–10) works on logs written by AdvancedAnalysis notebooks 0–2, and AdvancedAnalysis notebooks 3-1 and 3-3 read logs written by baseline step 6. All intermediate files are included in the repository, so each step can also be run on its own.

1. Install dependencies from `requirements.txt`.
2. Generate event logs, or extract the provided ones:
   - Generate new event logs with `EventLogGenerators/xes-creator-per-folder-all-types.ipynb` (for each parliament, edit the `folderPath` and `outputFilename` variables in the first cell). Use `xes-creator-per-folder-and-type.ipynb` instead if you only want a single process type (also edit the `vtyp` variable). Alternatively:
     Extract the `.xes.zip` files from `EventLogs/` into a folder `all-data-xes/`.
3. Explore the process types contained in the event logs with `BaselineAnalysis/type-explorer.ipynb`.
4. Create and explore performance measure results with `BaselineAnalysis/performance-measures.ipynb`. Change the `performanceMeasure` variable to switch between measures (cycle time, inter-arrival time, frequency, variants).
5. Run AdvancedAnalysis notebooks 0–2 (see [AdvancedAnalysis pipeline](#advancedanalysis-pipeline)) to create the lawmaking event logs enriched with topics and agreement scores, `AdvancedAnalysis/data-xes/<State>-with-topics-and-agreement-scores-all-time.xes`. Their input, the lawmaking traces containing a law draft in `AdvancedAnalysis/data-start/`, is provided pre-filtered.
6. Use `BaselineAnalysis/LawmakingAnalysis/preprocessing_comparisons.ipynb` for Baden-Württemberg and Brandenburg to introduce distinct activity labels (e.g. per reading) and make them more comparable across parliaments. It writes `AdvancedAnalysis/data-xes/<State>-with-topics-and-agreement-scores-all-time-preprocessed.xes`; edit the `INPUT_FILENAME`/`OUTPUT_FILENAME` variables per state.
7. Use `BaselineAnalysis/LawmakingAnalysis/my_case_log_builder.ipynb` to build per-case CSV logs (`cases_*.csv`, already included in `BaselineAnalysis/LawmakingAnalysis/`). Its inputs, `AdvancedAnalysis/data-xes/*-3EP-lawDraft-passedBills.xes`, are provided pre-filtered (with PM4Py) to the three most recent complete election periods and to traces that contain a law draft and lead to a passed bill. Edit the input/output filename variables at the top of the notebook.
8. Use `BaselineAnalysis/LawmakingAnalysis/difference_explorer.ipynb` to explore basic differences between the three states' case logs.
9. Use `BaselineAnalysis/LawmakingAnalysis/outcome_explorer.ipynb` to explore the distribution of lawmaking outcomes (delayed vs. in time).
10. Use `BaselineAnalysis/LawmakingAnalysis/hypothesis_inducer.ipynb` and `hypothesis_tester.ipynb` to induce and test rules explaining outcomes. The inducer lets you hide attributes from rule induction; if testing a manually derived rule fails, check whether the activity order matches how it was generated.
11. Continue with AdvancedAnalysis notebooks 3-1 to 3-4-1 (see [AdvancedAnalysis pipeline](#advancedanalysis-pipeline)) for the political-context enrichment and classification stage.

## AdvancedAnalysis Pipeline

`AdvancedAnalysis/` is seeded from `data-start/` (pre-filtered lawmaking event logs per state, containing only traces with a law draft) and the bundled Wahl-O-Mat dataset in `2025-03-26_Wahl-O-Mat-Datensaetze/`. Run the numbered notebooks in order. Between notebook 2 and notebooks 3-1/3-3, run `BaselineAnalysis/LawmakingAnalysis/preprocessing_comparisons.ipynb` for Baden-Württemberg and Brandenburg (step 6 above): it writes the `*-all-time-preprocessed.xes` logs that 3-1 and 3-3 read for these two states. Note that the pre-generated `data-csv/*-with-embeddings-allTime.csv.zip` files are also stored via Git LFS; notebook 1 regenerates them from `data-start/`.

| Notebook                                                                 | Reads                                                     | Writes                                                                       |
| ------------------------------------------------------------------------ | --------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `0-generate-wahl-o-mat-agreement-scores-and-topic-embeddings.ipynb`      | Wahl-O-Mat dataset (`2025-03-26_Wahl-O-Mat-Datensaetze/`) | `wahl-o-mat-agreement-scores/`, `wahl-o-mat-topic-embeddings/`               |
| `1-generate-event-logs-with-gesetzentwurf-topic-embeddings.ipynb`        | `data-start/*.xes`                                        | `data-csv/<State>-with-embeddings-allTime.csv` (git-ignored, see note below) |
| `2-generate-wahl-o-mat-feature-for-event-logs-all-time-projection.ipynb` | outputs of notebooks 0 and 1                              | `data-csv/`, `data-xes/*-with-topics-and-agreement-scores-all-time*.xes`     |
| `3-1-analysis-election-period-differences.ipynb`                         | `data-xes/` (`*-all-time-preprocessed.xes` for BW/BB)     | analysis/plots only                                                          |
| `3-2-analysis-wahl-o-mat-feature.ipynb`                                  | `data-xes/*-all-time.xes`                                 | analysis/plots only                                                          |
| `3-3-case-log-political-feature-enrichment.ipynb`                        | `data-xes/` (`*-all-time-preprocessed.xes` for BW/BB)     | `data-csv/case-logs/*.csv`                                                   |
| `3-4-0-analysis-logistic-regression-exploration.ipynb`                   | `data-csv/case-logs/*.csv` (single state)                 | analysis and plots (`.png`)                                                  |
| `3-4-1-k-fold-classification.ipynb`                                      | `data-csv/case-logs/*.csv` (all states)                   | analysis only                                                                |

Notebook 0 computes, for each Wahl-O-Mat thesis, a party-agreement (cohesion) score among government, opposition, and all parliamentary parties, projects these scores back onto earlier election periods, and generates topic embeddings for the theses. Notebook 1 embeds each legislative case's text (draft title, abstract, descriptors). Notebook 2 matches each case to its most similar Wahl-O-Mat thesis by embedding cosine similarity and attaches the corresponding agreement scores and similarity value as case attributes. Notebooks 3-1/3-2 analyze the resulting enriched logs (election-period patterns, agreement-score correlations); 3-3 flattens them into enriched per-case CSVs via `helper_enriching.py`, adding the _in-data_ features (draft authorship, author count, topic classification, legislative workload at case start) and _out-of-data_ features (election period, election-year flag, half-year index, government/opposition party counts and seat shares, law-draft PDF size, Wahl-O-Mat agreement scores and thesis similarity) described in the paper. 3-4-0 is an exploratory logistic-regression analysis for a single state. 3-4-1 produces the delay-classification results of the paper: restricted to passed bills from the three most recent complete election periods, it compares seven feature sets (control flow, in-data, out-of-data, and their combinations) with 15 classifiers and two baselines under stratified 10-fold cross-validation (ROC-AUC as primary metric; macro F1 with the decision threshold tuned in an inner cross-validation), tests CF against CF+In, CF+Out, and CF+Pol with paired Wilcoxon signed-rank tests (Holm-corrected), and runs a nested L1 feature selection whose stable features form the per-parliament feature table.

> **Runtime note:** notebook 3-3 downloads the law-draft PDF for every case one at a time (via `helper_enriching.add_pdf_case_attributes`/`get_pdf_information`) to derive the PDF-size/word-count features. Running this enrichment from scratch across all cases can therefore take a long time. Downloaded PDFs are cached in `AdvancedAnalysis/data-pdf-cache/` (git-ignored), so reruns only fetch PDFs that are not cached yet; URLs that failed to download are listed in `data-pdf-cache/failed_urls.txt`.
>
> Notebook 3-4-1 also takes a while to run: the Gaussian Process classifier and, above all, the nested feature selection (inner cross-validation over 20 L1 strengths per outer fold, for every state and feature set) dominate its runtime.

The `exploration-*.ipynb` notebooks are earlier scratch/prototype versions of steps 0 and the PDF-based enrichment idea; they are superseded by the numbered notebooks and `helper_enriching.py` and are kept only for reference.

Shared helper modules in `AdvancedAnalysis/`:

- `constants.py` – election years, election-period start dates, passed-bill activity names, and per-state government/opposition coalition definitions by date.
- `helper.py` – agreement-score computation and the embeddings API client used by notebooks 0 and 1.
- `helper_enriching.py` – per-case in-data/out-of-data feature functions (authorship, legislative workload, election period/year/half-year, coalition seat shares, cached PDF fetching and size/word-count), used by notebook 3-3.
- `dtree_helper.py` – extracts human-readable rules from a trained decision tree (also duplicated in `BaselineAnalysis/LawmakingAnalysis/` for the baseline rule induction step).
- `plotting.py` – agreement-score, heatmap, and embedding-PCA plotting helpers.

## Data & Licensing

Unless otherwise noted, source code in this repository is licensed under the **MIT License**, and generated/processed datasets under **CC BY 4.0**; see the `license` file for full terms. Raw data in `OriginalData/` is attributed to the respective parliaments' documentation services.

The Wahl-O-Mat dataset bundled under `AdvancedAnalysis/2025-03-26_Wahl-O-Mat-Datensaetze/` is © Bundeszentrale für politische Bildung and is **not** covered by the above license: per the accompanying `Hinweis.txt`, its use is otherwise prohibited except for analysis for scientific or journalistic purposes and publication of that analysis, provided it remains clear that the Bundeszentrale für politische Bildung is not the author of the analysis. Building a Wahl-O-Mat-like offering from this data is explicitly prohibited.

## Acknowledgments

Part of the code in `BaselineAnalysis/LawmakingAnalysis/` (rule induction) is reused from hvoelzer (2025), hvoelzer/outcomeanalysis: promise (promise), Zenodo, https://doi.org/10.5281/zenodo.15703293 — licensed under **CC BY 4.0**.
