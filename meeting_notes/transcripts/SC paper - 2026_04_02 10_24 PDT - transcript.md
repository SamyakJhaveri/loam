Apr 2, 2026

## SC paper \- Transcript

### 00:00:00

   
**Niranjan Hasabnis:** Yeah.  
**Samyak Jhaveri:** So what we have to do is find two or three corners of benchmarks from our raw data from our raw results where we identify the benefits of augmentation in the sense  
**Niranjan Hasabnis:** Mhm.  
**Samyak Jhaveri:** that the quality of the model output reduces in any of the metrics including build fail, run fail, verify fail and pass because at increasing levels of augmentation from L0 to L4, we see that the model is less capable of writing correct parallel  
**Niranjan Hasabnis:** Right.  
**Samyak Jhaveri:** code. We just have to find two three benchmark examples for that in order to uh dismiss lassi or any other bench benchmark. Uh that's task number one.  
**Niranjan Hasabnis:** Mhm.  
**Samyak Jhaveri:** Task number two is uh making sure to create graphs of those trends so that we have a visual representation of what is actually happening uh and add that to the intro and motivation section and everywhere else in the results and discussion section. task  
**Niranjan Hasabnis:** But I'll say it's a lower priority.  
**Samyak Jhaveri:** number.  
**Niranjan Hasabnis:** I mean I think yeah finding the motivating examples will be important one graphs I think is okay.  
   
 

### 00:01:08

   
**Samyak Jhaveri:** Yeah, of course.  
**Niranjan Hasabnis:** Yeah.  
**Samyak Jhaveri:** Yeah. Uh,  
**Niranjan Hasabnis:** Very good time,  
**Samyak Jhaveri:** so the data is definitely there. We just have to find a way to present it better in the paper.  
**Niranjan Hasabnis:** right?  
**Samyak Jhaveri:** Task number two is adding the GPT data by running the GPT vals as soon as possible.  
**Niranjan Hasabnis:** Mhm.  
**Samyak Jhaveri:** Uh task number three is um looking at the tables and seeing which ones are relevant and which ones are not. And for the ones that are relevant uh make sure that the column labeling and the captions are correct so that it is more intuitive to understand. Um and verify the the data presented in them based on the ground reality  
**Niranjan Hasabnis:** Mhm.  
**Samyak Jhaveri:** data that we have.  
**Niranjan Hasabnis:** Yeah, I think that is more of a writing thing. Yeah, but I think we'll we'll address that as we so read the paper more.  
**Samyak Jhaveri:** Yeah, of course. So, do you think there is more tasks any any more tasks to  
**Niranjan Hasabnis:** Um but do we have any table that shows the that evaluates the  
   
 

### 00:02:02

   
**Samyak Jhaveri:** do?  
**Niranjan Hasabnis:** benchmark itself like a independently in like some quantitative way like how many kernels are there like lines of code complexity wise or something?  
**Samyak Jhaveri:** No. What would you expect? Like what what is what what should it look  
**Niranjan Hasabnis:** Um yeah I mean  
**Samyak Jhaveri:** like?  
**Niranjan Hasabnis:** like if you have the different language support right maybe interesting way would be to understand like which version of koda do we support how much diversity do we have similarly for other APIs right because um if it is But yeah, I mean I understand this no may not be like easy to get that number but you're saying what I'm saying like I'm basically thinking like how do you show that the benchmark is like comprehensive um that it's not focused on only one version of CUDA but it has support for all the CUDA features that are out there possibly not may not be the latest one but most commonly used  
**Samyak Jhaveri:** H. So yes, the manif the remember the two-tier manifest we had. So the manifest has information to the make files and the make files will return for this one.  
   
 

### 00:03:32

   
**Samyak Jhaveri:** So anytime you add a new benchmark to the uh to this one, it will normalize it to use a specific CUDA version that is recommended.  
**Niranjan Hasabnis:** Okay.  
**Samyak Jhaveri:** And uh all of that information about running anything to make it comprehensive, to make it intuitive to use is mentioned in the manifest um uh files, which is like the two-tier thing. I could always if it's not there I could always add it to the paper where it says how are we making this a comprehensive benchmark which is reproducible and works with new kernels like standardizing the CUDA information version  
**Niranjan Hasabnis:** Okay.  
**Samyak Jhaveri:** information and so on I  
**Niranjan Hasabnis:** Do you think it's easy to get this information like in terms of  
**Samyak Jhaveri:** can try it's a good point I can All  
**Niranjan Hasabnis:** Okay.  
**Samyak Jhaveri:** right.  
**Niranjan Hasabnis:** Um but yeah I mean essentially I was this is all about understanding the benchmark quantitatively right in terms of uh language like feature support complexity also you can think of it like in terms of maybe lines of code right across different kernels. So like we have few kernels which are small in size, few which are large in size and what is the largest that we have.  
   
 

### 00:04:53

   
**Niranjan Hasabnis:** So some statistical analysis of the benchmark itself I think it will be useful. Um  
**Samyak Jhaveri:** Okay. So,  
**Niranjan Hasabnis:** yeah.  
**Samyak Jhaveri:** size of the kernels uh in terms of lines of code uh more statistical information about the programs and also um  
**Niranjan Hasabnis:** Yeah, I'm mentioning it here in my right.  
**Samyak Jhaveri:** the versions. Yeah.  
**Niranjan Hasabnis:** Um,  
**Samyak Jhaveri:** Yes, the uh multi thing. So there are some that are inherently multiile kernels. How we are addressing that is quite an interesting engineering approach.  
**Niranjan Hasabnis:** Mhm.  
**Samyak Jhaveri:** So we should emphasize on um how we are handling single file to single file and multifile to single and so on all those permutation combinations.  
**Niranjan Hasabnis:** Mhm.  
**Samyak Jhaveri:** Uh I think that would be a strong point because reviewers will point out if you are trying to standardize all of these kernels all of these different different APIs into one benchmark.  
**Niranjan Hasabnis:** All  
**Samyak Jhaveri:** How are you making sure that the LLM is being evaluated on the kernel writing capacity  
**Niranjan Hasabnis:** right.  
**Samyak Jhaveri:** and not the capacity to write helper functions which is peripheral.  
   
 

### 00:06:06

   
**Samyak Jhaveri:** So I think emphasizing that is very important.  
**Niranjan Hasabnis:** Mhm.  
**Samyak Jhaveri:** So, I'm just wording it out because I want to have all of this in notes and I can just get help with  
**Niranjan Hasabnis:** Yeah.  
**Samyak Jhaveri:** uh writing it.  
**Niranjan Hasabnis:** No,  
**Samyak Jhaveri:** So,  
**Niranjan Hasabnis:** I'm not taking the notes. I'll share it with you.  
**Samyak Jhaveri:** yeah.  
**Niranjan Hasabnis:** Um, yeah, but think about some other I think the the language feature, the single files and multifile. Um, yeah. So the these are essentially the if you think about it these are the highlights of the benchmark right and we should basically bring this point also in the introduction if you haven't done that already um I can also take care like I will read the paper and then look at that from that angle if you're missing something to highlight because that way is easy to distinguish our benchmark than existing ones right  
**Samyak Jhaveri:** from existing ones. Exactly. So that's the thing.  
**Niranjan Hasabnis:** Yeah,  
**Samyak Jhaveri:** We took our sweet time to think of all the limitations of other benchmarks and we have engineered it into there.  
   
 

### 00:07:04

   
**Niranjan Hasabnis:** right.  
**Samyak Jhaveri:** It is a matter presenting it in a way that people realize it like this that  
**Niranjan Hasabnis:** Yeah. So then I mean that's why this analysis will be useful,  
**Samyak Jhaveri:** we've done this Yeah,  
**Niranjan Hasabnis:** right?  
**Samyak Jhaveri:** exactly.  
**Niranjan Hasabnis:** If you it should basically provide quantitative like a numbers for the for  
**Samyak Jhaveri:** Exactly.  
**Niranjan Hasabnis:** the highlights that we are going to present. So um because without that then it's just a matter of yeah it will be a more of a subject to them. People need to read and then or look at the bench for themselves but if you have the data already  
**Samyak Jhaveri:** Exactly. So,  
**Niranjan Hasabnis:** um right across  
**Samyak Jhaveri:** we have to bring that up to the front where people most likely need it.  
**Niranjan Hasabnis:** language. So you can think of this as a table in a sense like you have one column for like one language like coda one for openmpp um and then across for and then we have like rows which says the number of like the language feature supported um I think yeah I mean it will be useful if we can find out like what is the lowest language like what is the lowest API version that we support right and how the highest one but I think it will be much more complex to actually so I want to say basically like the way that we support open MP  
   
 

### 00:08:16

   
**Niranjan Hasabnis:** 1.0 all the way up to open MP 5.0 right so all of the we have benchmark consider I mean has all the features from all the across all the versions but it will be yeah I mean much more involved analysis unless  
**Samyak Jhaveri:** It's very complex to track that down.  
**Niranjan Hasabnis:** you  
**Samyak Jhaveri:** I can try, of course. It's very complex because all of these benchmarks come from different timelines of when they were created and when they were updated.  
**Niranjan Hasabnis:** Yeah, but I think if you can just simply grape for the Openmp  
**Samyak Jhaveri:** There are times when Yeah.  
**Niranjan Hasabnis:** APIs and then you will need I think getting that list will not be that hard. You will need to see like yeah I mean find out an API for open 5.0 and open 1.0 zero and then see whether both of them are present. Right?  
**Samyak Jhaveri:** Yeah.  
**Niranjan Hasabnis:** That way you can  
**Samyak Jhaveri:** Yeah. There were Yeah,  
**Niranjan Hasabnis:** actually  
**Samyak Jhaveri:** there were times when uh the same benchmark, same repository, different kernels, different versions of CUDA.  
   
 

### 00:09:14

   
**Niranjan Hasabnis:** Yeah.  
**Samyak Jhaveri:** So they worked with different and they did not work for the newer version also.  
**Niranjan Hasabnis:** Like  
**Samyak Jhaveri:** I mean it's it's a little complex but I think it's definitely easy to get that information get see how how how much of that we can get.  
**Niranjan Hasabnis:** Right. Okay. Uh, sounds good. Anything I think? Yeah. Looks  
**Samyak Jhaveri:** I think that's good iterations good number of homework for me right now. I'll start and get to it right now.  
**Niranjan Hasabnis:** good. Yeah. Yeah.  
**Samyak Jhaveri:** Yeah.  
**Niranjan Hasabnis:** I'll go over the paper and then if there's something missing, I will let you know. But I think overall looks looks in pretty good shape actually. Yeah.  
**Samyak Jhaveri:** Yes. Okay, let's do  
**Niranjan Hasabnis:** I mean um Yeah. Yeah,  
**Samyak Jhaveri:** it.  
**Niranjan Hasabnis:** I mean I haven't I think seen a benchmark paper in a while. So I think this is a I think I'm writing this after a while. So I think it's a good question on your  
   
 

### 00:10:01

   
**Samyak Jhaveri:** You can you can go through the references to see the latest ones like you can  
**Niranjan Hasabnis:** end.  
**Samyak Jhaveri:** just type in 2025 or so and you know you'll be a you'll be up to date. It's very interesting the kind of work that people do and they're selectively trying to sell their benchmark like we are also trying to sell our benchmark but sometimes they're very conveniently getting rid of some things that should  
**Niranjan Hasabnis:** Yeah, that's that's always the case with the scientific benchmarking,  
**Samyak Jhaveri:** there  
**Niranjan Hasabnis:** right? I mean, you selectively choose best for your case. Yeah, there was a paper on the topic also,  
**Samyak Jhaveri:** yeah but overall All it's good to know that  
**Niranjan Hasabnis:** I think.  
**Samyak Jhaveri:** there is work to do in this in this domain that even frontier LLMs today are not able to write the best possible parallel  
**Niranjan Hasabnis:** Right. Right. Yeah.  
**Samyak Jhaveri:** code  
**Niranjan Hasabnis:** That's uh but I think so far does the result tells the story that that tell that story or is that I think co is doing overall better.  
   
 

### 00:11:02

   
**Samyak Jhaveri:** I  
**Niranjan Hasabnis:** Do do results actually show?  
**Samyak Jhaveri:** forbench for our  
**Niranjan Hasabnis:** No no for the for our task the numbers or are the results showing that story or are the results  
**Samyak Jhaveri:** task.  
**Niranjan Hasabnis:** showing that the LLMs are doing very well?  
**Samyak Jhaveri:** the I mean I think you don't draw a line with one point you need to draw you need to have two points to draw a line so I think once we get GPD data we'll know uh  
**Niranjan Hasabnis:** No,  
**Samyak Jhaveri:** how if it's actually doing well or is it just expected to be operating at this level  
**Niranjan Hasabnis:** I mean it's a it could be either way. I mean I mean if they're doing well that's fine.  
**Samyak Jhaveri:** Yeah.  
**Niranjan Hasabnis:** I mean there is nothing wrong with that. I mean it's just a matter of like it's a like a independent evaluation,  
**Samyak Jhaveri:** Yeah.  
**Niranjan Hasabnis:** right? So if there is they're not doing well in the scope if they're doing well then yeah that's good actually for  
**Samyak Jhaveri:** Exactly.  
**Niranjan Hasabnis:** the HPC community  
   
 

### 00:11:55

   
**Samyak Jhaveri:** Exactly.  
**Niranjan Hasabnis:** right  
**Samyak Jhaveri:** They will know which models to use when they're developing HPC programs.  
**Niranjan Hasabnis:** yeah I mean it's uh I mean I I think making that point will be a bit harder because then you would need evaluation across most of the commonly used but I think The point that we can make is that our benchmark is comprehensive one and yeah I mean it's a benchmark paper not a LLM evaluation paper that's there's a distinction there right so don't read the paper  
**Samyak Jhaveri:** Mhm.  
**Niranjan Hasabnis:** to understand which LLM is doing better because that's not our paper is for right because  
**Samyak Jhaveri:** scope. No scope  
**Niranjan Hasabnis:** yeah yeah so right yeah but then you can actually read  
**Samyak Jhaveri:** name.  
**Niranjan Hasabnis:** the paper to understand how to go about evaluating the basically  
**Samyak Jhaveri:** Yeah,  
**Niranjan Hasabnis:** I think that is the um that is it's a subtle point but we should make  
**Samyak Jhaveri:** that's true. We're making the tool Yeah,  
**Niranjan Hasabnis:** right.  
**Samyak Jhaveri:** we're making the tool to understand other tools. We're not making We're not trying to improve those tools,  
   
 

### 00:12:59

   
**Niranjan Hasabnis:** Yeah.  
**Samyak Jhaveri:** right?  
**Niranjan Hasabnis:** Right.  
**Samyak Jhaveri:** Awesome.  
**Niranjan Hasabnis:** All right.  
**Samyak Jhaveri:** All right. Thank you so  
**Niranjan Hasabnis:** And I will uh send you the email that talks about the model like compute how to get  
**Samyak Jhaveri:** much.  
**Niranjan Hasabnis:** access or if you want I can show you maybe few minutes actually. Let me see if I can.  
**Samyak Jhaveri:** Are you also from Gujarat?  
**Niranjan Hasabnis:** Oh no, I'm from Pune actually.  
**Samyak Jhaveri:** Oh,  
**Niranjan Hasabnis:** How about  
**Samyak Jhaveri:** Gujarat. Gujarat.  
**Niranjan Hasabnis:** you?  
**Samyak Jhaveri:** I I I know some of my father's patients with the same surname as yours and I thought that you were also  
**Niranjan Hasabnis:** Oh, no, no, no. I think Yeah,  
**Samyak Jhaveri:** Gujarati.  
**Niranjan Hasabnis:** I think it's all u um I mean it's mixed,  
**Samyak Jhaveri:** It's everything mixed. Yeah, of course.  
**Niranjan Hasabnis:** right?  
**Samyak Jhaveri:** Yeah.  
**Niranjan Hasabnis:** Find out how it is sign basically.  
**Samyak Jhaveri:** I think I'll go over the email.  
**Niranjan Hasabnis:** Okay.  
**Samyak Jhaveri:** I need to meet my advisor today in like 5 10 minutes.  
**Niranjan Hasabnis:** Oh yeah, sure. It It's not that difficult actually.  
**Samyak Jhaveri:** So that's okay.  
**Niranjan Hasabnis:** Yeah. Yeah. Sounds good. So I think all that you need is raw access to the GPU, right? Oh yeah. Yeah. Right. So raw raw access is very much possible actually and you can choose whatever GP you want. I have bunch of available. Yeah. All right. Sounds good then. Okay. See you then. Bye-bye.  
   
 

### Transcription ended after 00:15:07

*This editable transcript was computer generated and might contain errors. People can also change the text after it was created.*