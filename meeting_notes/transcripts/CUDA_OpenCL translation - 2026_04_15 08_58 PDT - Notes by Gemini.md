Apr 15, 2026

## CUDA:OpenCL translation

Invited [talkad@post.bgu.ac.il](mailto:talkad@post.bgu.ac.il) [Niranjan Hasabnis](mailto:niranjan@codemetal.ai) [tbitan@gmail.com](mailto:tbitan@gmail.com) [Armand Mousavi](mailto:armand@codemetal.ai) [thelechen@gmail.com](mailto:thelechen@gmail.com) [Matthew Freihofer](mailto:matt@codemetal.ai) [Sanjna Ravichandar](mailto:sanjna@codemetal.ai) [inbalc2@mail.tau.ac.il](mailto:inbalc2@mail.tau.ac.il) [gbolet@vt.edu](mailto:gbolet@vt.edu) [samyaknj@uci.edu](mailto:samyaknj@uci.edu) [erel.kaplan@campus.technion.ac.il](mailto:erel.kaplan@campus.technion.ac.il) [avrahame@campus.technion.ac.il](mailto:avrahame@campus.technion.ac.il) [yosefgoren@campus.technion.ac.il](mailto:yosefgoren@campus.technion.ac.il) [prema@uab.edu](mailto:prema@uab.edu) [le.chen@anl.gov](mailto:le.chen@anl.gov) [galoren@technion.ac.il](mailto:galoren@technion.ac.il) [roee.bar@campus.technion.ac.il](mailto:roee.bar@campus.technion.ac.il) ~~[Peter Morales](mailto:peter@codemetal.ai)~~ ~~[Octavian Udrea](mailto:octavian@codemetal.ai)~~ ~~[Laura Titolo](mailto:laura@codemetal.ai)~~

Attachments [CUDA:OpenCL translation](https://calendar.google.com/calendar/event?eid=N21sNzhjMTNubDZramgxa24xbHN1MHF0djZfMjAyNjA0MjJUMTYwMDAwWiBuaXJhbmphbkBjb2RlbWV0YWwuYWk) [Notes - CUDA:OpenCL translation](https://docs.google.com/document/d/11A3E8Y9KIh1sZWI-o48st5IlRwpw2h___V904G656bk/edit)

Meeting records [Recording](https://drive.google.com/file/d/1syNqc2W2-CbabWbD7EWmvCrLVPhjIKwE/view?usp=drive_web) 

### Summary

Discussion focused on the next phase of distributed computing projects with updates on PowerBench and latent guidance research.

**Distributed Computing and Domain Decomposition**  
The strategic focus shifted beyond Parcodex to tackling distributed computing, identifying domain decomposition and synchronization reasoning as the next critical problems. The team must prove an autonomous agent can change code and reason about synchronization for tightly coupled simulations.

**Addressing Parcodex Limitations and Efficiency**  
Discussion centered on identifying Parcodex’s limits for improvement and the need for open-source alternatives to Codex for broader accessibility. Efficiency improvements should focus on an ensemble model approach, utilizing small models like Gemma 4 as a coordinator for larger LLMs for heavy lifting.

**Latent Guidance Research Presentation**  
Preliminary results for the latent guidance research showed a noticeable performance improvement, with the validation rate increasing 2.5% across 40 kernels using a Partial Reward Model. The team agreed on the necessity of checking two tracks for the Supercomputing submission: the best open-source model and the best proprietary model.

### Next steps

- [ ] \[Samyak Jhaveri\] Submit Testing Plan: Send a full 1-page table plan detailing testing execution, included models, comparison metrics, required token, and compute resources by end of the week.

- [ ] \[Gal Oren, Niranjan Hasabnis\] Review Testing Plan: Review Samyak's detailed 1-page table plan. Approve compute resources, including GPT access and machine time, necessary for experiments.

- [ ] \[Tomer Bitan\] Email Feedback: Send re-evaluation feedback and issues found during external testing via email. CC all group members on the communication.

- [ ] \[Gal Oren\] Test Evaluation Script: Test the Powerbench evaluation process on a different GPU hardware. Attempt to recreate issues found by Tomer after receiving his feedback.

- [ ] \[Tomer Bitan\] Verify Codes: Look at exact output codes. Verify passed codes match extraction successes.

- [ ] \[Tomer Bitan\] Conduct Testing: Use the new cleaner data batch to create a better PRM version. Try evaluating performance using PowerBench augmentation data. Analyze the existing self-repair run results.

- [ ] \[Tomer Bitan\] Share Link: Send the link to the meeting presentation slides.

- [ ] \[Tomer Bitan\] Email Paper Point: Send a clear email explaining the main point for the paper draft.

- [ ] \[Tomer Bitan\] Report PowerBench: Send an email or Discord message detailing any issues found with the PowerBench script. Report issues before Friday or Saturday morning.

- [ ] \[Tomer Bitan\] Submit Paper Draft: Verify evaluation numbers and send the draft of the paper to the group by the weekend.

### Details

* **Introductions and Acknowledging Success**: The meeting began with general greetings among Niranjan Hasabnis, lian ghrayeb, Prema Soundararajan, and Gal Oren, noting that Lei will not be joining but a note-taker is present. Gal Oren commended the team for the acceptance of the ACL paper, describing the work as a "great paper" that is receiving improvements due to current actions. Samyak Jhaveri joined the discussion, and the conversation turned to the continuation of the work.

* **Discussing the Next Step Beyond Parcodex**: Gal Oren suggested contemplating the next steps after Parcodex, noting that autonomous code agents are proven to parallel code, though more testing and benchmarks might be needed. They reminded the team of previous work on distribution computing, differentiating it from parallel computing, which involves distributing computation across multiple nodes or devices before parallelizing it. Gal Oren highlighted that Parcodex focused on the "conquering of the parallel section," but the distributed section is the bigger problem to address next.

* **Focusing on Domain Decomposition and Code Change**: The next critical problem involves proving that an autonomous agent can perform domain decomposition and synchronization between different devices or nodes. This work would require the autonomous agent to literally change the code, creating a new version of the code rather than just adding pragmas, and reasoning about the needed synchronization, which is critical for tightly coupled simulations. They emphasized the difficulty of this task, noting that a suitable benchmark for domain decomposition does not currently exist.

* **Proposing New Benchmarks for Distributed Computing**: Gal Oren suggested two approaches to tackle the lack of benchmarks for distributed computing: creating a "Disbench" by traversing literature to find codes with serial and MPI versions (like a version of Lules code) or taking serial or OpenMP versions from existing benchmarks (like Hebench) and having the model perform domain decomposition. The latter approach would involve checking numerical and runtime differences against the work divided by the number of devices to establish a ground proof based on Gustafson's law. Gal Oren emphasized that they are already contemplating the "real imminent next step" even though immediate tasks like PowerBench, Parcodex, and Tomer Bitan's work still need to be concluded.

* **Identifying Limitations and Accessibility for Parcodex**: Niranjan Hasabnis expressed interest in understanding the limits of Parcodex, suggesting that if the best models like Codex fail, it provides a chance for improvement and helps define the limitation section of the paper. They also suggested that to make the research more accessible, the team should explore building a smaller, open-source model that performs as well as Codex, which would be a significant contribution since the current software is of limited use unless people have access to Codex.

* **Exploring Alternatives to Codex and Improved Efficiency**: Gal Oren noted that the team has not fully explored what open-source models can do, or other proprietary models, citing limitations related to money and effort, as the work is currently tightly coupled to the mini version of Codex. Erel Kaplan suggested that efficiency could be improved not through fine-tuning, but by changing how the coding agent passes context and history between turns. Erel Kaplan also proposed exploring the concept of a small model calling a larger model as a tool for critical parts, citing a paper by Anthropic.

* **Proposing an Ensemble Model Approach for Tool Use**: Samyak Jhaveri proposed using an ensemble of models, suggesting that the locally hosted Gemma 4 model could act as the cheaper tool coordinator to call tools, including a higher large language model (LLM) like Opus for heavy lifting and intelligence. They also suggested using a graph RAG approach, such as the one in Obsidian, to manage context, store information, and minimize context rot. Niranjan Hasabnis questioned whether model-level improvements would provide new results in terms of quality or merely engineering efficiency, noting that writing a paper is difficult if the latter is the case.

* **Addressing Benchmark Concerns for Supercomputing Submission**: Gal Oren confirmed that they will need to check the reasoning stages for the Supercomputing submission, and offered access to Codex reasoning models and GPT 4.1. They suggested checking two tracks: the best open-source model (like Llama or Gemma) and the best proprietary model, using various levels of checkups, including direct model output and reasoning models over the benchmark. Samyak Jhaveri stated that the complete setup for the script is ready with the Quen 3.5 model and suggested using GPT 5.4 with thinking enabled as the second model, noting that compute is needed for building, running, and verifying the parallel programs.

* **Establishing a Plan for Experiment Reruns**: Samyak Jhaveri was asked to submit a one-page plan by the end of the week detailing the testing process, including which models will be included, how the comparison will be conducted, and the needed tokens and compute. Samyak Jhaveri confirmed that the script and infrastructure are ready, requiring only parameter changes for a new experiment, and expressed concern about the high number of benchmarks, though Gal Oren insisted on keeping the roughly 100 kernels to maintain convincing statistical coverage. The team decided to generate new results for both Quen and GPT 5.4 with a new experimental design, including turning thinking on and reporting pass@3 instead of pass@1.

* **Reviewing Feedback from External Evaluation**: Tomer Bitan shared feedback from their external evaluation of PowerBench, noting issues with environment variables, certain kernels, and code extraction. Erel Kaplan elaborated that one issue was a "static method of extracting the code from the LLM response" which led to extraction failures when the LLM did not follow the expected format. Gal Oren stressed that this feedback is critical, emphasizing the importance of making the benchmark usable on different hardware setups, and requested that Tomer Bitan share all feedback via email.

* **Presenting Research on Latent Guidance for Code Translation**: Tomer Bitan presented their fundamental research project, "latent guidance for parallel code translation," which aims to tackle the cost and specialization issues identified in previous work. The methodology involves moving to latent reasoning (using hidden state abstract vectors instead of full tokens for thought) and employing a "process reward model" that guides the model's reasoning process during inference to provide specialization without full fine-tuning. Tomer Bitan explained the data set construction involves branching latent thought vectors, adding noise, and aggregating scores from an evaluation framework to train a small 7B Quen Coder model to predict the potential quality of the reasoning.

* **Preliminary Performance Improvement with PRM**: Tomer Bitan presented preliminary results showing a noticeable performance improvement, specifically in the validation rate when using a PRM (Partial Reward Model). The validation rate increased by times two and 5% across about 40 kernels, with the main difference coming from the Palbench data set. Tomer Bitan acknowledged that the improvement is not as large as hoped but is visible and expects the difference to enlarge with more testing and correct extraction of all results.

* **PRM Efficiency and Token Usage**: The initial findings on efficiency were described as disappointing, particularly with the UNIPL data set, where adding PRM did not noticeably boost performance compared to latent reasoning alone when using 15,000 maximum output tokens. However, lowering the maximum tokens to 9,000 for the UNIPL data set did not affect performance, which suggests PRM is helpful for balancing efficiency and performance, but it does not provide a clear picture of the desired performance boost.

* **Upcoming Work and Future Experiments**: Tomer Bitan outlined plans to verify the outputted code for accuracy, use a cleaner batch of data to create a better PRM, and try using the anonymized data for Palbench to utilize all its available original kernels. An additional run with self-repair is planned to demonstrate that the method remains sustained and efficient when using an agent.

* **Immediate Follow-up and Conclusion of Meeting**: Gal Oren noted the meeting was past time and requested Tomer Bitan to immediately send an email with the presentation link and a clear text explanation of the points for the paper. Gal Oren instructed Tomer Bitan to send the email so that others could react to the material asynchronously due to Gal Oren having another meeting to attend.

* **Discussion on Baseline Model for Comparison**: Niranjan Hasabnis suggested that it would be beneficial to include a baseline Llama 3.3 model without latent reasoning in the graphs for comparison, as the current results were taken from the original Uni paper. Tomer Bitan agreed that this is a good idea, though it would require rerunning the original Llama on the Palbench data.

* **Analyzing Performance Improvement and Paper Submission**: Tomer Bitan questioned if the current performance difference is sufficient for a paper submission, given that the paper is currently oriented around the PRM. Niranjan Hasabnis advised that the magnitude of the numbers is not as critical as being able to analyze and reason why the improvement occurs and how it is derived from the features.

* **Fixing PalBench Script Issues**: Samyak Jhaveri requested that Tomer Bitan send a report detailing any issues found with PalBench, preferably by the end of the week, so that they can fix the script before running further evaluations. Tomer Bitan acknowledged that there were issues related to the CUDA version numbers which they had attempted to resolve using different environments.

* **Evaluation Using Augmented Data**: Tomer Bitan asked about the validity of evaluating on anonymized (augmented) data that was trained on, noting that this method leaves only about 20 kernels for evaluation otherwise. Niranjan Hasabnis advised keeping the evaluation numbers from the augmented data set separate from the test set results; if the numbers appear similar, they could potentially be combined.

* **Paper Draft and Evaluation Resources**: Tomer Bitan informed Niranjan Hasabnis that most of the paper draft is complete and plans to send the verified numbers and the draft by the weekend. Tomer Bitan also confirmed they are still using the Modal platform for evaluation runs, which Niranjan Hasabnis confirmed is acceptable following consultation with their IT contact.

*You should review Gemini's notes to make sure they're accurate. [Get tips and learn how Gemini takes notes](https://support.google.com/meet/answer/14754931)*

*How is the quality of **these specific notes?** [Take a short survey](https://google.qualtrics.com/jfe/form/SV_9vK3UZEaIQKKE7A?confid=mFsXttSbGNpUYMlHWwXdDxIYOAIIigIgARgBCA&detailid=standard&screenshot=false) to let us know your feedback, including how helpful the notes were for your needs.*