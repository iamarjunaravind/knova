# 200 Quality Verbal Ability Questions

def get_verbal_questions():
    questions = []

    # 1. Synonyms (20 questions)
    syn_scenarios = [
        ("Choose the word that is most nearly SYNONYMOUS in meaning to 'METICULOUS'.", "Thorough", "Careless", "Hasty", "Casual"),
        ("Select the closest synonym for 'RESILIENT'.", "Adaptable", "Fragile", "Rigid", "Vulnerable"),
        ("What is the synonym of 'UBIQUITOUS'?", "Omnipresent", "Scarce", "Unique", "Temporary"),
        ("Choose the word closest in meaning to 'PRAGMATIC'.", "Practical", "Theoretical", "Idealistic", "Fanciful"),
        ("Which word is synonymous with 'CANDID'?", "Frank", "Deceptive", "Reserved", "Guarded"),
        ("Find the synonym for 'EPHEMERAL'.", "Transitory", "Eternal", "Enduring", "Perpetual"),
        ("What is the meaning closest to 'TENACIOUS'?", "Persistent", "Yielding", "Weak", "Fickle"),
        ("Choose the best synonym for 'LUCID'.", "Clear", "Obscure", "Vague", "Murky"),
        ("Which word is closest in meaning to 'MITIGATE'?", "Alleviate", "Aggravate", "Intensify", "Worsen"),
        ("Select the synonym of 'AFFLUENT'.", "Wealthy", "Impoverished", "Destitute", "Needy"),
        ("What is the synonym for 'BENEVOLENT'?", "Kind", "Malevolent", "Spiteful", "Hostile"),
        ("Choose the closest synonym for 'CANDOR'.", "Honesty", "Insincerity", "Deceit", "Pretense"),
        ("Which word is synonymous with 'DILIGENT'?", "Hardworking", "Lazy", "Neglectful", "Inattentive"),
        ("Find the synonym of 'DISPARITY'.", "Inequality", "Similarity", "Harmony", "Likeness"),
        ("What is the synonym of 'EXEMPLARY'?", "Commendable", "Flawed", "Mediocre", "Inferior"),
        ("Select the word closest in meaning to 'INNOVATIVE'.", "Original", "Conventional", "Derivative", "Traditional"),
        ("Choose the synonym for 'OBSOLETE'.", "Outdated", "Contemporary", "Modern", "Current"),
        ("What word is closest in meaning to 'PERVASIVE'?", "Widespread", "Isolated", "Rare", "Confined"),
        ("Choose the synonym for 'PROFOUND'.", "Deep", "Superficial", "Shallow", "Trivial"),
        ("Which word is synonymous with 'VINDICATE'?", "Exonerate", "Accuse", "Condemn", "Blame"),
    ]
    for q, c, w1, w2, w3 in syn_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 2. Antonyms (20 questions)
    ant_scenarios = [
        ("Choose the word that is most nearly OPPOSITE in meaning to 'TRANSPARENT'.", "Opaque", "Lucid", "Clear", "Translucent"),
        ("Select the antonym for 'BENEVOLENT'.", "Malevolent", "Generous", "Charitable", "Compassionate"),
        ("What is the opposite of 'FRUGAL'?", "Extravagant", "Economical", "Thrifty", "Prudent"),
        ("Choose the antonym for 'DORMANT'.", "Active", "Sleeping", "Latent", "Inactive"),
        ("Which word is the antonym of 'CONCEAL'?", "Reveal", "Hide", "Cover", "Disguise"),
        ("Select the antonym of 'AFFLUENCE'.", "Poverty", "Wealth", "Opulence", "Prosperity"),
        ("What is the opposite of 'EXPEDITE'?", "Delay", "Accelerate", "Hasten", "Quicken"),
        ("Choose the antonym of 'ZENITH'.", "Nadir", "Peak", "Apex", "Summit"),
        ("Which word is the antonym of 'VERBOSE'?", "Concise", "Wordy", "Long-winded", "Talkative"),
        ("Select the antonym for 'RIGID'.", "Flexible", "Stiff", "Unyielding", "Firm"),
        ("What is the opposite of 'HOSTILE'?", "Friendly", "Aggressive", "Antagonistic", "Belligerent"),
        ("Choose the antonym for 'AMATEUR'.", "Professional", "Novice", "Beginner", "Learner"),
        ("Which word is the antonym of 'OPTIMISTIC'?", "Pessimistic", "Hopeful", "Confident", "Positive"),
        ("Select the antonym for 'SCARCITY'?", "Abundance", "Deficiency", "Dearth", "Shortage"),
        ("What is the opposite of 'VOLUNTARY'?", "Compulsory", "Optional", "Willing", "Elective"),
        ("Choose the antonym for 'VACILLATE'?", "Decide", "Hesitate", "Waver", "Fluctuate"),
        ("Which word is the opposite of 'SERENE'?", "Agitated", "Calm", "Peaceful", "Tranquil"),
        ("Select the antonym of 'PRODIGAL'?", "Frugal", "Wasteful", "Reckless", "Lavish"),
        ("What is the opposite of 'TRANSIENT'?", "Permanent", "Temporary", "Fleeting", "Short-lived"),
        ("Choose the antonym for 'SKEPTICAL'?", "Convinced", "Doubting", "Distrustful", "Suspicious"),
    ]
    for q, c, w1, w2, w3 in ant_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 3. Idioms & Phrases (20 questions)
    idiom_scenarios = [
        ("What is the meaning of the idiom 'To bite the bullet'?", "To face an inevitable grim situation with courage", "To chew on metal", "To avoid a conflict", "To fire a weapon hastily"),
        ("What does 'To burn the midnight oil' mean?", "To work or study late into the night", "To waste precious fuel", "To start a dangerous fire", "To sleep past midday"),
        ("What is the meaning of 'A blessing in disguise'?", "An apparent misfortune that yields unexpected positive results", "A hidden danger", "A secret gift from a mentor", "A religious ceremony"),
        ("What does 'Hit the nail on the head' signify?", "To describe exactly what is causing a situation", "To hammer accurately", "To miss an opportunity", "To hurt oneself while working"),
        ("The expression 'Spill the beans' means:", "To reveal a secret prematurely", "To drop groceries", "To cook food carelessly", "To confess under police interrogation"),
        ("What does 'Piece of cake' refer to?", "Something that is very easy to accomplish", "A sweet bakery confection", "A complex multi-step assignment", "A celebratory gathering"),
        ("What is meant by 'Under the weather'?", "Feeling slightly ill or unwell", "Caught in a heavy rainstorm", "Forecasting meteorological changes", "Suffering from sunstroke"),
        ("What does 'Once in a blue moon' denote?", "An event that happens very rarely", "Every full lunar cycle", "A common daily occurrence", "A celestial eclipse"),
        ("The idiom 'Costs an arm and a leg' means:", "Extremely expensive", "Physically injurious", "A medical surgery", "Fair market value"),
        ("What does 'To see eye to eye' mean?", "To agree entirely with someone", "To engage in a staring contest", "To have identical vision", "To confront an enemy directly"),
        ("What does 'Break the ice' mean in social settings?", "To initiate conversation and relieve social tension", "To crack winter frost", "To prepare cold beverages", "To cause an uncomfortable silence"),
        ("The phrase 'Take it with a grain of salt' means:", "To view something with a degree of skepticism", "To add seasoning to a meal", "To reject advice completely", "To accept blindly"),
        ("What does 'Cut corners' mean in business?", "To perform a task improperly to save time or money", "To trim edges of packaging", "To make sharp turns", "To negotiate ethically"),
        ("The idiom 'Devil's advocate' refers to someone who:", "Argues against a position to provoke debate", "Defends unethical practices", "Engages in criminal law", "Refuses to express an opinion"),
        ("What is meant by 'Cry over spilled milk'?", "To lament over past occurrences that cannot be undone", "To clean up dairy accidents", "To request an apology", "To complain about fair rules"),
        ("The idiom 'Best of both worlds' implies:", "An ideal situation enjoying two distinct advantages", "Travelling across continents", "Living between reality and fantasy", "Possessing dual citizenship"),
        ("What does 'Back to the drawing board' signify?", "Starting planning over after a prior attempt failed", "Purchasing architectural blueprints", "Practicing sketch artistry", "Cancelling all future meetings"),
        ("The expression 'Steal someone's thunder' means:", "To take credit for someone else's achievement or ideas", "To create loud noises", "To interrupt a weather broadcast", "To rob someone violently"),
        ("What does 'Barking up the wrong tree' mean?", "Pursuing a mistaken line of thought or action", "A confused guard dog", "Climbing dangerous branches", "Blaming an innocent animal"),
        ("The idiom 'Through thick and thin' means:", "Under all conditions, regardless of difficulties", "Growing physically larger", "Walking through forests", "Traveling long distances"),
    ]
    for q, c, w1, w2, w3 in idiom_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 4. Sentence Correction & Grammar (20 questions)
    gram_scenarios = [
        ("Identify the correct sentence:", "Neither the professor nor the students were satisfied with the syllabus.", "Neither the professor nor the students was satisfied with the syllabus.", "Neither the professor or the students were satisfied with the syllabus.", "Neither the professor nor the students is satisfied with the syllabus."),
        ("Choose the grammatically correct sentence:", "She has been working here since 2021.", "She is working here since 2021.", "She was working here since 2021.", "She had worked here since 2021."),
        ("Identify the correct form of the pronoun: 'Between you and ___, this strategy will work.'", "me", "I", "myself", "mine"),
        ("Which sentence uses parallel structure correctly?", "He likes swimming, running, and cycling.", "He likes to swim, running, and to cycle.", "He likes swimming, to run, and cycling.", "He likes swim, run, and cycling."),
        ("Choose the sentence with correct subject-verb agreement:", "A bouquet of yellow roses was delivered this morning.", "A bouquet of yellow roses were delivered this morning.", "A bouquet of yellow roses have been delivered this morning.", "A bouquet of yellow roses are delivered this morning."),
        ("Identify the error in: 'Each of the participants [A] must submit [B] their [C] portfolio by Friday [D].'", "their (should be 'his or her')", "Each of", "must submit", "by Friday"),
        ("Select the correct conditional sentence:", "If I were you, I would accept the scholarship offer.", "If I was you, I would accept the scholarship offer.", "If I am you, I will accept the scholarship offer.", "If I had been you, I will accept the scholarship offer."),
        ("Choose the correct passive voice: 'The team completed the research.'", "The research was completed by the team.", "The research had completed by the team.", "The research is completed by the team.", "The research was being completed by the team."),
        ("Identify the correctly punctuated sentence:", "Although it was raining, we decided to go hiking.", "Although it was raining we decided to go hiking.", "Although it was raining; we decided to go hiking.", "Although, it was raining, we decided to go hiking."),
        ("Choose the sentence with the correct modifier placement:", "Walking into the room, she noticed the broken vase on the floor.", "Walking into the room, the broken vase was noticed by her on the floor.", "Walking into the room, on the floor the broken vase was noticed.", "The broken vase was noticed on the floor walking into the room."),
        ("Select the correct preposition: 'He is capable ___ solving complex analytical equations.'", "of", "to", "for", "in"),
        ("Identify the correct modal verb: 'You ___ wear a safety helmet on a construction site.'", "must", "might", "can", "may"),
        ("Choose the correct word: 'The company's new policies had a positive ___ on employee productivity.'", "effect", "affect", "affective", "effection"),
        ("Select the correct comparative form: 'This proposal is ___ than the previous draft.'", "more comprehensive", "comprehensiver", "most comprehensive", "more comprehensively"),
        ("Identify the sentence with correct apostrophe usage:", "The students' textbooks were kept in the locker room.", "The student's textbooks were kept in the locker room (plural).", "The students textbooks were kept in the locker room.", "The students's textbooks were kept in the locker room."),
        ("Choose the correct sentence:", "Scarcely had he entered the laboratory when the fire alarm rang.", "Scarcely had he entered the laboratory than the fire alarm rang.", "Scarcely he had entered the laboratory then the fire alarm rang.", "Scarcely did he entered the laboratory when the fire alarm rang."),
        ("Select the sentence with no redundancy:", "He returned home at 6 PM.", "He returned back home at 6 PM.", "He reverted back home at 6 PM.", "He returned back to home at 6 PM."),
        ("Choose the correct form: 'The committee ___ divided in their opinions.'", "were", "was", "is", "has been"),
        ("Identify the sentence using the subjunctive mood correctly:", "The dean insisted that every candidate be on time.", "The dean insisted that every candidate is on time.", "The dean insisted that every candidate was on time.", "The dean insisted that every candidate will be on time."),
        ("Select the sentence with correct verb tense:", "By the time the conference concludes tomorrow, the keynote speaker will have delivered three lectures.", "By the time the conference concludes tomorrow, the keynote speaker will deliver three lectures.", "By the time the conference concludes tomorrow, the keynote speaker had delivered three lectures.", "By the time the conference concludes tomorrow, the keynote speaker is delivering three lectures."),
    ]
    for q, c, w1, w2, w3 in gram_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 5. One-Word Substitution (20 questions)
    sub_scenarios = [
        ("A person who loves books and collects them avidly:", "Bibliophile", "Philatelist", "Polyglot", "Numismatist"),
        ("A person who speaks or writes several languages fluently:", "Polyglot", "Monoglot", "Linguist", "Orator"),
        ("One who knows everything:", "Omniscient", "Omnipotent", "Omnipresent", "Invincible"),
        ("A person who walks in their sleep:", "Somnambulist", "Noctambulist", "Insomniac", "Narcissist"),
        ("One who donates money and resources to help those in need:", "Philanthropist", "Misanthrope", "Mercenary", "Ascetic"),
        ("A person who dislikes human society and avoids people:", "Misanthrope", "Philanthropist", "Extrovert", "Altruist"),
        ("A remedy that is believed to cure all diseases:", "Panacea", "Placebo", "Antidote", "Antibiotic"),
        ("Something that cannot be avoided or escaped:", "Inevitable", "Incorrigible", "Infallible", "Inaudible"),
        ("A person who looks on the bright side of things:", "Optimist", "Pessimist", "Pragmatist", "Cynic"),
        ("An animal that feeds entirely on plants:", "Herbivore", "Carnivore", "Omnivore", "Insectivore"),
        ("A doctor who specializes in the treatment of heart disorders:", "Cardiologist", "Neurologist", "Dermatologist", "Pediatrician"),
        ("Government by a single ruler with absolute authority:", "Autocracy", "Democracy", "Oligarchy", "Anarchy"),
        ("The study of the origins and history of words:", "Etymology", "Entomology", "Epistemology", "Eschatology"),
        ("A handwritten or typed document before it is published:", "Manuscript", "Scripture", "Transcript", "Postscript"),
        ("A person who has reached the age of one hundred years or more:", "Centenarian", "Octogenarian", "Nonagenarian", "Sexagenarian"),
        ("A person who flees from justice or persecution:", "Fugitive", "Vagrant", "Exile", "Refugee"),
        ("The practice of having more than one spouse at the same time:", "Polygamy", "Monogamy", "Bigamy", "Endogamy"),
        ("A person who creates maps and nautical charts:", "Cartographer", "Choreographer", "Calligrapher", "Topographer"),
        ("A post or position with high salary but little or no real work:", "Sinecure", "Honourary", "Freelance", "Apprenticeship"),
        ("A speech delivered without any prior preparation:", "Extempore", "Monologue", "Dialogue", "Soliloquy"),
    ]
    for q, c, w1, w2, w3 in sub_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 6. Prepositions & Phrasal Verbs (20 questions)
    prep_scenarios = [
        ("The delegates agreed ___ the terms laid out in the bilateral treaty.", "to", "with", "on", "in"),
        ("He was accused ___ orchestrating the security breach.", "of", "with", "for", "about"),
        ("She congratulated her colleague ___ winning the academic scholarship.", "on", "for", "with", "at"),
        ("Students are advised to refrain ___ using mobile phones during the lecture.", "from", "of", "to", "in"),
        ("The new operating policy is contrary ___ our organizational principles.", "to", "with", "against", "from"),
        ("The laboratory is fully equipped ___ modern analytical instruments.", "with", "of", "by", "for"),
        ("He is thoroughly adept ___ resolving technical disputes.", "in", "to", "with", "for"),
        ("The startup finally broke ___ the international enterprise market.", "into", "through", "out", "away"),
        ("The university committee decided to call ___ the annual convocation due to bad weather.", "off", "out", "away", "up"),
        ("She takes ___ her grandmother in both appearance and demeanor.", "after", "to", "up", "with"),
        ("Please look ___ this statistical report before the morning briefing.", "over", "into", "at", "after"),
        ("The team managed to come ___ with an ingenious software solution.", "up", "in", "along", "down"),
        ("He was exempted ___ attending the physical orientation program.", "from", "of", "with", "for"),
        ("The scientist attributes her groundbreaking discovery ___ years of rigorous experimentation.", "to", "for", "with", "in"),
        ("They arrived ___ the international airport early in the morning.", "at", "in", "to", "on"),
        ("This historic monument dates back ___ the seventeenth century.", "to", "from", "in", "into"),
        ("She was completely absorbed ___ reading the quantum mechanics manual.", "in", "with", "at", "on"),
        ("The security guards were instructed to adhere strictly ___ the emergency protocols.", "to", "with", "for", "on"),
        ("The project's success is contingent ___ securing administrative funding.", "upon", "for", "with", "to"),
        ("He decided to give ___ smoking to improve his cardiovascular stamina.", "up", "in", "out", "away"),
    ]
    for q, c, w1, w2, w3 in prep_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 7. Analogies (20 questions)
    ana_scenarios = [
        ("SCALPEL : SURGEON :: CHISEL : ?", "Sculptor", "Painter", "Carpenter", "Architect"),
        ("TELESCOPE : ASTRONOMER :: MICROSCOPE : ?", "Biologist", "Chemist", "Geologist", "Historian"),
        ("CANVAS : PAINTER :: BLUEPRINT : ?", "Architect", "Sculptor", "Photographer", "Editor"),
        ("OAR : BOAT :: PEDAL : ?", "Bicycle", "Automobile", "Airplane", "Train"),
        ("MELODY : COMPOSER :: NOVEL : ?", "Author", "Actor", "Director", "Publisher"),
        ("THERMOMETER : TEMPERATURE :: BAROMETER : ?", "Pressure", "Humidity", "Wind speed", "Rainfall"),
        ("SEEDS : PLANT :: SAPLING : ?", "Tree", "Fruit", "Leaf", "Forest"),
        ("GRAIN : SILO :: WATER : ?", "Reservoir", "Aquifer", "Pipe", "Well"),
        ("CLOCK : TIME :: ODOMETER : ?", "Distance", "Speed", "Fuel", "Acceleration"),
        ("NEEDLE : THREAD :: PEN : ?", "Ink", "Paper", "Notebook", "Pencil"),
        ("COMPASS : DIRECTION :: BALANCE : ?", "Weight", "Volume", "Height", "Length"),
        ("BRICK : WALL :: CELL : ?", "Tissue", "Atom", "Organism", "Nucleus"),
        ("FRICTION : HEAT :: COMBUSTION : ?", "Energy", "Cooling", "Friction", "Smoke"),
        ("BIRD : AVIARY :: BEE : ?", "Apiary", "Aquarium", "Hive", "Kennel"),
        ("JUDGE : COURTROOM :: SCIENTIST : ?", "Laboratory", "Library", "Clinic", "Observatory"),
        ("AUTHOR : FOREWORD :: COMPOSER : ?", "Overture", "Encore", "Cadenza", "Finale"),
        ("EPILOGUE : PLAY :: POSTSCRIPT : ?", "Letter", "Book", "Speech", "Poem"),
        ("STETHOSCOPE : PHYSICIAN :: TROWEL : ?", "Mason", "Plumber", "Electrician", "Mechanic"),
        ("VACCINE : PREVENTION :: MEDICINE : ?", "Cure", "Diagnosis", "Infection", "Allergy"),
        ("LIGHT : REFRACTION :: SOUND : ?", "Echo", "Volume", "Frequency", "Amplitude"),
    ]
    for q, c, w1, w2, w3 in ana_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 8. Spelling & Vocabulary in Context (20 questions)
    spell_scenarios = [
        ("Identify the correctly spelled academic term:", "Accommodate", "Acommodate", "Accomodate", "Acomodate"),
        ("Which of the following words is spelled correctly?", "Conscientious", "Consciencious", "Conscientous", "Conscensious"),
        ("Choose the correct spelling:", "Liaison", "Liason", "Liasion", "Laision"),
        ("Select the correctly spelled word:", "Privilege", "Priviledge", "Privilege", "Privelege"),
        ("Identify the correct spelling:", "Questionnaire", "Questionaire", "Questionair", "Questionnare"),
        ("Which word is spelled correctly?", "Separate", "Seperate", "Seprate", "Seperite"),
        ("Choose the correctly spelled word:", "Embarrass", "Embarass", "Emberrass", "Emberas"),
        ("Identify the correct spelling:", "Millennium", "Millenium", "Milenium", "Milennium"),
        ("Select the correct spelling:", "Supersede", "Supercede", "Superseed", "Supercede"),
        ("Which of the following is spelled correctly?", "Cemetery", "Cemetary", "Semetary", "Cemitary"),
        ("Choose the correctly spelled word:", "Maintenance", "Maintainance", "Maintenence", "Maintanence"),
        ("Identify the correct spelling:", "Hierarchy", "Heirarchy", "Hierarcy", "Heirarcy"),
        ("Select the correct spelling:", "Maneuver", "Maneuvre", "Maneuver", "Manuver"),
        ("Which of the following is spelled correctly?", "Occurrence", "Occurence", "Occurrance", "Ocurrence"),
        ("Choose the correct spelling:", "Pronunciation", "Pronounciation", "Pronuntiation", "Prononciation"),
        ("Identify the correct spelling:", "Pharaoh", "Pharoah", "Faroh", "Pharao"),
        ("Select the correctly spelled word:", "Indispensable", "Indispensible", "Indespensable", "Indespensible"),
        ("Choose the correct spelling:", "Definite", "Definately", "Defanite", "Definate"),
        ("Which word is spelled correctly?", "Perseverance", "Perseverence", "Persevirence", "Perserverance"),
        ("Identify the correctly spelled word:", "Noticeable", "Noticable", "Noticeble", "Noticible"),
    ]
    for q, c, w1, w2, w3 in spell_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 9. Reading Comprehension & Inferences (20 questions)
    rc_scenarios = [
        ("Passage: 'Renewable energy adoption has accelerated as battery storage technology matures.' What is the author's primary assertion?", "Energy storage improvements enable broader renewable adoption", "Fossil fuels are entirely obsolete today", "Battery storage is environmentally hazardous", "Renewable sources cannot meet global peak demand"),
        ("Passage: 'Artificial intelligence enhances diagnostic radiology, yet human clinicians remain essential for empathetic decision-making.' What is the author's tone?", "Balanced and objective", "Hostile toward technological advances", "Overly pessimistic", "Indifferent and dismissive"),
        ("Passage: 'Global urbanisation demands intelligent transit infrastructures to avert crippling congestion.' The term 'crippling' most nearly means:", "Severely debilitating", "Physically injuring", "Temporary", "Inconsequential"),
        ("Passage: 'Empirical research confirms that multilingual individuals demonstrate superior cognitive flexibility.' Which deduction is most valid?", "Learning languages supports versatile mental processing", "Monoglot speakers experience cognitive decay", "Language learning is effortless for all adults", "Vocabulary size is proportional to intelligence"),
        ("Passage: 'The digital divide is no longer just about hardware access; it now encompasses algorithmic literacy.' What does the author imply?", "Understanding how digital tools operate is now vital", "Computers should be provided free to all schools", "Hardware costs have ceased to matter", "Software engineering must be taught in kindergarten"),
        ("Passage: 'Micro-credentials offer agile pathways for professionals to upskill without completing multi-year degrees.' The primary benefit highlighted is:", "Flexibility and efficiency in learning", "Lower academic rigor", "Guaranteed corporate executive appointments", "Immediate obsolescence of standard university degrees"),
        ("Passage: 'Despite initial resistance, peer-reviewed open-access publishing has expanded academic dissemination globally.' What was the impact of open-access?", "Broader international reach of scientific knowledge", "Diminished quality of peer reviews", "Immediate financial bankruptcy of journals", "Restricted access to verified research"),
        ("Passage: 'Ethical governance of autonomous systems requires cross-disciplinary collaboration between engineers, ethicists, and legal scholars.' The author suggests that:", "Engineering solutions alone are insufficient for tech ethics", "Only lawyers understand autonomous machinery", "Ethicists should manage software development teams", "AI technology must be halted immediately"),
        ("Passage: 'Ecosystem restoration projects succeed only when local indigenous communities are recognized as primary stewards.' The key factor for success is:", "Empowerment and involvement of local communities", "Increased international tourism revenues", "Exclusively federal government intervention", "Introduction of non-native plant species"),
        ("Passage: 'Critical thinking requires questioning assumptions, examining evidence, and acknowledging cognitive biases.' What is essential for critical thinking?", "Self-awareness of one's own biases and evidence inspection", "Quick intuitive judgments", "Memorizing established textbooks", "Unconditional agreement with authority figures"),
        ("Passage: 'Telecommuting has blurred the boundary between domestic leisure and vocational commitment.' The author notes that working from home:", "Often obscures the distinction between personal and work time", "Has reduced overall corporate productivity", "Is disliked by all employees", "Eliminates the requirement for work schedules"),
        ("Passage: 'The resilience of global supply chains depends more on diversification of suppliers than on cost minimization.' The author argues in favor of:", "Spreading sourcing across multiple varied suppliers", "Cutting procurement expenses at all costs", "Restricting suppliers to a single domestic market", "Ending global trade agreements"),
        ("Passage: 'Neuroplasticity demonstrates that adult brains retain the capacity to reorganize neural pathways through deliberate practice.' What does this imply?", "Lifelong cognitive learning remains biologically viable", "Brain structure is completely fixed after adolescence", "Deliberate practice causes irreversible neural fatigue", "Memory retention declines uniformly after age twenty"),
        ("Passage: 'Modern democracies thrive when public discourse is informed by verified factual reporting rather than sensationalist commentary.' The author values:", "Factual integrity over sensationalized headlines", "State-controlled media broadcast censorship", "Elimination of opinion journalism", "Anonymous social media commentary"),
        ("Passage: 'Sustainable architecture prioritizes passive heating and cooling to reduce reliance on energy-intensive HVAC systems.' What is the focus?", "Designing structures that leverage natural climate dynamics", "Eliminating windows in modern skyscrapers", "Increasing electricity consumption", "Building exclusively with concrete materials"),
        ("Passage: 'The precautionary principle advises against implementing emergent technologies before their long-term environmental hazards are known.' The principle recommends:", "Exercising prudence and thorough safety testing prior to deployment", "Rejecting all technological innovations", "Unrestricted commercial launch without regulation", "Restricting research to theoretical models"),
        ("Passage: 'Data privacy regulations like GDPR empower users by giving them explicit control over personal information collected by corporations.' The regulation's core goal is:", "Restoring individual authority over private data", "Banning internet advertising completely", "Mandating daily password renewals", "Government ownership of internet servers"),
        ("Passage: 'Financial literacy curricula in secondary schools significantly reduce predatory debt vulnerability in young adults.' What is the direct outcome?", "Lower likelihood of falling into unmanageable debt", "Immediate qualification for mortgage loans", "Guaranteed high-paying corporate employment", "Complete elimination of income tax obligations"),
        ("Passage: 'Space exploration catalyzes domestic innovations, yielding civilian spin-offs from medical imaging sensors to water filtration systems.' The author argues that:", "Space research generates valuable cross-industry benefits on Earth", "Space missions are an unjustifiable public expense", "Commercial space flight should be outlawed", "Astronauts should focus entirely on planetary defense"),
        ("Passage: 'Interdisciplinary scientific research bridges traditional silos, yielding breakthroughs at the intersection of biology, computing, and materials science.' The author advocates for:", "Collaborative inquiry across distinct academic domains", "Strengthening boundaries between science disciplines", "Funding only computer science departments", "Ending theoretical physics funding"),
    ]
    for q, c, w1, w2, w3 in rc_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 10. Foreign Phrases & Literary Devices (20 questions)
    lit_scenarios = [
        ("What is the meaning of the Latin phrase 'STATUS QUO'?", "The existing state of affairs", "A drastic revolution", "A legal summons", "A written treaty"),
        ("The term 'BONA FIDE' translates literally to:", "In good faith / Genuine", "Without proof", "Of unknown origin", "Under protest"),
        ("What does the Latin phrase 'AD HOC' mean?", "Created for a specific purpose or case", "Permanent and universal", "From ancient tradition", "Without legal sanction"),
        ("What is a 'PERSONA NON GRATA'?", "An unwelcome or unacceptable individual", "A famous dignitary", "A distinguished scholar", "An anonymous diplomat"),
        ("The Latin phrase 'CARPE DIEM' translates into English as:", "Seize the day", "Live and let live", "Time flies", "Remember death"),
        ("What does 'QUID PRO QUO' denote?", "A favor or advantage granted in return for something", "A legal paradox", "A question without an answer", "An equal financial split"),
        ("What is the literary device in: 'The wind whispered secrets through the trees'?", "Personification", "Hyperbole", "Simile", "Oxymoron"),
        ("Identify the literary device in: 'She was as brave as a lion in the face of danger.'", "Simile", "Metaphor", "Alliteration", "Irony"),
        ("Which figure of speech is found in: 'I have told you a million times to double-check your code'?", "Hyperbole", "Understatement", "Metaphor", "Paradox"),
        ("What figure of speech is demonstrated by the phrase 'DEAFENING SILENCE'?", "Oxymoron", "Onomatopoeia", "Euphemism", "Metonymy"),
        ("What is an 'ALLITERATION'?", "The repetition of initial consonant sounds in neighboring words", "An exaggerated statement", "A humorous play on words", "A comparison without 'like' or 'as'"),
        ("The phrase 'Passed away' used instead of 'Died' is an example of:", "Euphemism", "Hyperbole", "Irony", "Satire"),
        ("What is a 'PARADOX'?", "A statement that appears contradictory but reveals a deeper truth", "A statement that is demonstrably false", "An insult disguised as a compliment", "A rhyming couplet"),
        ("What does the Latin phrase 'DE FACTO' mean?", "Existing in reality, regardless of whether recognized by law", "Formally enacted by parliament", "Under appeal in high court", "Proven to be fraudulent"),
        ("What does 'IN SITU' mean in scientific and archaeological contexts?", "In its original or natural place", "In an artificial laboratory", "Under vacuum pressure", "In a secondary habitat"),
        ("Identify the device: 'The buzzing bee flew across the sizzling barbecue.'", "Onomatopoeia", "Metaphor", "Personification", "Apostrophe"),
        ("What does the phrase 'MODUS OPERANDI' denote?", "A characteristic way or method of working", "A musical composition", "An architectural blueprint", "A sudden flash of insight"),
        ("What does the Latin expression 'PRIMA FACIE' mean?", "Based on the first impression / Accepted until proven otherwise", "At the conclusion of trial", "Without any witnesses", "Behind closed doors"),
        ("What is an 'ANALOGY'?", "A comparison between two different things based on shared characteristics", "A formal apology", "A grammatical contradiction", "A type of rhythmic verse"),
        ("The phrase 'Time is a thief' is an example of which figure of speech?", "Metaphor", "Simile", "Synecdoche", "Alliteration"),
    ]
    for q, c, w1, w2, w3 in lit_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    return questions
