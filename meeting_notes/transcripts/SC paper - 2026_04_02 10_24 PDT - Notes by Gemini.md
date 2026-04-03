Apr 2, 2026

## SC paper

Invited [Niranjan Hasabnis](mailto:niranjan@codemetal.ai) [le.chen@anl.gov](mailto:le.chen@anl.gov) [samyaknj@uci.edu](mailto:samyaknj@uci.edu)

Attachments [SC paper](https://www.google.com/calendar/event?eid=MGx0ZGt1bGFwNjU0ajRxNWJrNzBnbTJvdjEgbmlyYW5qYW5AY29kZW1ldGFsLmFp) 

Meeting records [Transcript](?tab=t.bbgadbwltq3u) 

### Summary

The meeting prioritized identifying augmentation benefits and emphasized quantitative benchmark analysis for paper quality.

**Identify Augmentation Benefits**  
The most important task is to identify 2 or 3 corner benchmarks that show decreased model output quality as augmentation levels increase from L0 to L4. These motivating examples must demonstrate the model's reduced capability to write correct parallel code with increasing augmentation levels.

**Quantitative Benchmark Analysis**  
Statistical analysis of the benchmark is necessary to demonstrate comprehensiveness, including metrics like the number of kernels and lines of code. This quantitative data will support the claims about the benchmark's highlights and complexity.

**Paper Scope Clarification**  
The paper is a benchmark paper focused on creating a comprehensive evaluation tool, not an LLM evaluation paper determining which LLM is superior. Emphasis must be placed on the engineering approach used for kernel conversions to address reviewer scrutiny regarding evaluation focus.

### Details

* **Identifying Benefits of Augmentation**: The first task involves identifying two or three corner benchmarks from the raw results where augmentation benefits are evident, particularly where model output quality decreases across metrics like build fail, run fail, verify fail, and pass, as augmentation levels increase from L0 to L4. The goal is to find benchmark examples that demonstrate the model's reduced capability to write correct parallel code with increasing augmentation levels. Niranjan Hasabnis noted that finding these motivating examples is the most important task, considering the creation of corresponding graphs a lower priority ([00:00:00](?tab=t.bbgadbwltq3u#heading=h.s6vrocvpcv1i)).

* **Data Visualization and GPT Data Integration**: Samyak Jhaveri identified two tasks: creating graphs to visually represent the identified trends of augmentation impact and adding them to the introductory, motivation, results, and discussion sections of the paper ([00:00:00](?tab=t.bbgadbwltq3u#heading=h.s6vrocvpcv1i)). The next task is to incorporate GPT data by running the GPT evaluations as soon as possible ([00:01:08](?tab=t.bbgadbwltq3u#heading=h.3f7rofnihxd6)).

* **Table Review and Clarity**: Samyak Jhaveri outlined a task to review the tables in the paper, determine their relevance, and ensure that relevant tables have correct column labeling and intuitive captions. This task also involves verifying the data presented in the tables against the ground reality data they possess, although Niranjan Hasabnis suggested this is a writing task that can be addressed as they read the paper more ([00:01:08](?tab=t.bbgadbwltq3u#heading=h.3f7rofnihxd6)).

* **Quantitative Benchmark Analysis**: The discussion shifted to the need for a quantitative evaluation of the benchmark itself, potentially including metrics like the number of kernels, lines of code, or complexity ([00:02:02](?tab=t.bbgadbwltq3u#heading=h.i8p0zst8ilyj)). Niranjan Hasabnis suggested that statistical analysis of the benchmark, such as the size of kernels in terms of lines of code and feature support across different API versions, would be useful to demonstrate the benchmark's comprehensiveness ([00:03:32](?tab=t.bbgadbwltq3u#heading=h.obemebja986c)). Samyak Jhaveri agreed that gathering statistical information on kernel size and program statistics is a good point ([00:04:53](?tab=t.bbgadbwltq3u#heading=h.2nsyzn3sjm7k)).

* **Highlighting Benchmark Engineering and Complexity**: A key point raised by Samyak Jhaveri was the need to emphasize the engineering approach used to handle single-file to single-file and multi-file to single-file kernel conversions when standardizing various APIs into one benchmark. This emphasis is considered a strong point because reviewers are likely to question how the benchmark ensures the LLM is evaluated on kernel writing capacity rather than peripheral helper function writing ([00:04:53](?tab=t.bbgadbwltq3u#heading=h.2nsyzn3sjm7k)). Niranjan Hasabnis affirmed that these points are the highlights of the benchmark and should be included in the introduction to distinguish it from existing benchmarks ([00:06:06](?tab=t.bbgadbwltq3u#heading=h.qtoe8bef6cpw)).

* **Presenting Quantitative Data for Benchmark Highlights**: Niranjan Hasabnis stressed that the proposed quantitative analysis would provide the necessary data and numbers to support the highlights and claims made about the benchmark's comprehensiveness. Samyak Jhaveri acknowledged that they need to bring this quantitative data to the forefront of the paper ([00:07:04](?tab=t.bbgadbwltq3u#heading=h.jmt4kvmog0my)). The complexity of tracking API version support was discussed, specifically using OpenMP 1.0 up to OpenMP 5.0 as an example of version coverage ([00:08:16](?tab=t.bbgadbwltq3u#heading=h.nqu08i22fhju)).

* **Final Task Summary and Paper Review**: The participants concluded the discussion having established a good number of homework tasks for Samyak Jhaveri. Niranjan Hasabnis committed to reviewing the paper and notifying Samyak Jhaveri of any missing elements ([00:09:14](?tab=t.bbgadbwltq3u#heading=h.j10gnynzk2db)). The conversation touched upon the nature of scientific benchmarking, noting that practitioners often selectively choose the best results for their case ([00:10:01](?tab=t.bbgadbwltq3u#heading=h.eq2nsa7fsid3)).

* **Clarifying the Paper's Scope**: The discussion addressed whether the current results show that frontier large language models (LLMs) are not able to write the best parallel code, which Samyak Jhaveri noted will become clearer once the GPT data is available ([00:10:01](?tab=t.bbgadbwltq3u#heading=h.eq2nsa7fsid3)). Niranjan Hasabnis clarified that the paper is a benchmark paper, not an LLM evaluation paper, and the focus is on creating a comprehensive tool for evaluation, not on determining which LLM is superior ([00:11:55](?tab=t.bbgadbwltq3u#heading=h.nnmmrnz8aqr9)).

* **Accessing Compute Resources**: The meeting concluded with Niranjan Hasabnis offering to send an email about how to obtain compute access, specifically raw access to the GPU, which Samyak Jhaveri needed for running the GPT evaluations. Niranjan Hasabnis confirmed that raw access is possible and they have a selection of available GPUs ([00:12:59](?tab=t.bbgadbwltq3u#heading=h.u0n36x6bqg0q)).

### Suggested next steps

- [ ] \[Samyak Jhaveri\] Find Benchmarks: Identify 2-3 benchmark examples showing model quality reduction. Use these examples to dismiss competing benchmarks.

- [ ] \[Samyak Jhaveri\] Create Graphs: Generate visual graphs illustrating augmentation trends. Add graphs to introduction, motivation, results, and discussion sections.

- [ ] \[Samyak Jhaveri\] Run GPT Evaluation: Incorporate GPT data by running the GPT evaluations as soon as possible.

- [ ] \[Samyak Jhaveri\] Table Review: Review paper tables, determine relevance, and ensure correct column labels and captions for intuitive understanding. Verify table data accuracy based on ground reality data.

- [ ] \[Samyak Jhaveri\] Analyze Benchmark: Perform statistical analysis of the benchmark. Include kernel size (lines of code), program statistics, and support for language features like CUDA/OpenMP versions.

- [ ] \[Niranjan Hasabnis\] Read Paper: Review the paper content to identify any missing highlights. Focus specifically on aspects distinguishing the benchmark from existing ones.

- [ ] \[Niranjan Hasabnis\] Send Access Email: Send email documentation about model access and compute information, including obtaining raw GPU access.

*You should review Gemini's notes to make sure they're accurate. [Get tips and learn how Gemini takes notes](https://support.google.com/meet/answer/14754931)*

*Please provide feedback about using Gemini to take notes in a [short survey.](https://google.qualtrics.com/jfe/form/SV_9vK3UZEaIQKKE7A?confid=xLjPdgnKVyXjFKwqpdBsDxIWOAIIigIgARgBCA&detailid=standard)*