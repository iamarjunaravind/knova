# 200 Quality Logical Reasoning Questions

def get_logical_questions():
    questions = []

    # 1. Number & Alphabet Series (20 questions)
    series_scenarios = [
        ("Find the next number in the sequence: 4, 9, 16, 25, 36, ?", "49 (7^2)", "48", "50", "47"),
        ("What is the next number in the series: 3, 6, 12, 24, 48, ?", "96 (*2)", "92", "84", "100"),
        ("Identify the missing number: 2, 5, 10, 17, 26, ?", "37 (+11)", "35", "38", "36"),
        ("Complete the sequence: 80, 70, 61, 53, 46, ?", "40 (-6)", "41", "39", "42"),
        ("What comes next in the Fibonacci sequence: 1, 1, 2, 3, 5, 8, 13, ?", "21", "20", "22", "19"),
        ("Find the missing number in the alternating series: 7, 10, 8, 11, 9, 12, ?", "10", "11", "13", "8"),
        ("Complete the letter series: B, D, F, H, J, ?", "L (+2)", "K", "M", "N"),
        ("Find the next term in the sequence: Z, X, V, T, R, ?", "P (-2)", "Q", "O", "S"),
        ("What is the missing term: A1, C3, E5, G7, ?", "I9", "H8", "I8", "J10"),
        ("Complete the sequence: 1, 8, 27, 64, 125, ?", "216 (6^3)", "200", "225", "343"),
        ("Find the next number: 12, 23, 34, 45, 56, ?", "67 (+11)", "66", "68", "65"),
        ("What comes next in the series: 100, 96, 88, 76, 60, ?", "40 (-20)", "42", "38", "44"),
        ("Complete the letter series: AZ, BY, CX, DW, ?", "EV", "EU", "FU", "FW"),
        ("Find the next number: 2, 3, 5, 7, 11, 13, ?", "17 (Next Prime)", "15", "19", "16"),
        ("Identify the missing number: 5, 11, 23, 47, 95, ?", "191 (*2 + 1)", "190", "189", "192"),
        ("Complete the series: 6, 11, 21, 36, 56, ?", "81 (+25)", "76", "80", "85"),
        ("What comes next: CX, FU, IR, LO, ?", "OL", "PK", "OK", "NL"),
        ("Find the next number: 1, 4, 9, 18, 35, ?", "68 (*2 - n)", "70", "64", "72"),
        ("Complete the sequence: 31, 28, 31, 30, 31, 30, ?", "31 (Days in Months)", "28", "29", "30"),
        ("What is the missing term: 2, 6, 12, 20, 30, 42, ?", "56 (+14)", "54", "58", "52"),
    ]
    for q, c, w1, w2, w3 in series_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 2. Coding-Decoding (20 questions)
    code_scenarios = [
        ("If 'CLOUD' is coded as 'DMPVE' (+1 shift), how is 'RAIN' coded?", "SBJO", "SZJM", "TBKO", "RBJO"),
        ("In a certain code, 'LIGHT' is written as 'LIGTH' (last two letters swapped). How is 'STORM' written?", "STORMR" if False else "STOMR", "STORMS", "STROM", "SOTRM"),
        ("If A = 1, B = 2, C = 3, and CAT = 24 (3+1+20), what is the numerical code for 'DOG'?", "26 (4+15+7)", "28", "24", "30"),
        ("If 'BLUE' is coded as 'CKSF' (+1, -1, +1, -1), how will 'PINK' be coded?", "QHOJ", "QHNL", "QGMJ", "QIOJ"),
        ("In a code language, 'ROSE' is coded as '6821' and 'CHAIR' as '73456'. What is the code for 'SEARCH'?", "214673", "214763", "214637", "216473"),
        ("If 'APPLE' is written as 'ELPPA' (reversed), how is 'ORANGE' written?", "EGNARO", "EGNAOR", "ENGAOR", "EGONRA"),
        ("In a certain code language, if 'FIRE' is coded as 'DGPC' (-2 shift), how is 'WATER' coded?", "UYREP", "UZSFQ", "VZSDR", "TYREP"),
        ("If 'PEN' = 35 and 'PAGE' = 29, what is the value of 'BOOK' (2+15+15+11)?", "43", "45", "41", "39"),
        ("In a code, '123' means 'hot filtered coffee', '356' means 'very hot day', and '589' means 'day and night'. What digit stands for 'very'?", "6", "3", "5", "8"),
        ("If 'TABLE' is coded as 'GZYOV' (opposite alphabet pairs), what is the code for 'CHAIR'?", "XSZRI", "XTYRI", "WSZRI", "XSZQJ"),
        ("If 'TRAIN' is coded as 'WUDLQ' (+3 shift), how will 'BUS' be coded?", "EXV", "EYW", "DWU", "EZV"),
        ("In a code language, 'COMPUTER' is written as 'RFUVQNPC'. How is 'MEDICINE' written in that code?", "EOJDJEFM", "EOJDEJFM", "MFEJDJFM", "EOJDJEFN"),
        ("If 'SUN' is coded as '27' and 'MOON' as '57', what is 'STAR' (19+20+1+18)?", "58", "56", "60", "54"),
        ("If 'GOLD' is coded as 'HOME' (+1 shift), how is 'SILVER' coded?", "TJMWFS", "TJMWFT", "TIMWFS", "UKNXGT"),
        ("In a certain code, 'ZEBRA' is written as '26-5-2-18-1'. What is the code for 'COBRA'?", "3-15-2-18-1", "3-14-2-18-1", "3-15-2-19-1", "4-15-2-18-1"),
        ("If 'DELHI' is coded as 'CCIDD', how will 'BOMBAY' be coded?", "AMJXVS", "ALJXVS", "AMKXVT", "AMJXVT"),
        ("In a code, 'PENCIL' is written as 'LICNEP'. How is 'NOTEBOOK' written?", "KOOBETON", "KOOBENTO", "KOOBETNO", "KOBEOTON"),
        ("If 'RED' is called 'BLUE', 'BLUE' is called 'WHITE', 'WHITE' is called 'BLACK', what is the color of clear sky?", "WHITE", "BLUE", "BLACK", "RED"),
        ("If 'WATER' is called 'FOOD', 'FOOD' is called 'TREE', 'TREE' is called 'SKY', what does a fish swim in?", "FOOD", "WATER", "TREE", "SKY"),
        ("In a code, 'MONKEY' is written as 'XDJMNL'. How is 'TIGER' written in that code?", "QDFHS", "SDFHQ", "QDHER", "RFEHS"),
    ]
    for q, c, w1, w2, w3 in code_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 3. Blood Relations (20 questions)
    blood_scenarios = [
        ("Pointing to a photograph, John said, 'His mother is the only daughter of my mother.' Whose photograph was it?", "John's son", "John's nephew", "John's brother", "John himself"),
        ("A is the brother of B. B is the sister of C. D is the father of A. How is C related to D?", "Son or Daughter", "Brother", "Uncle", "Father"),
        ("Pointing to a lady, a man said, 'The son of her only brother is the brother of my wife.' How is the lady related to the man?", "Paternal Aunt", "Sister of father-in-law", "Mother-in-law", "Maternal Aunt"),
        ("Introducing a man, a woman said, 'He is the only son of my mother's mother.' How is the man related to the woman?", "Maternal Uncle", "Father", "Brother", "Cousin"),
        ("P is the father of Q and R is the son of S. T is the brother of P. If Q is the sister of R, how is S related to T?", "Sister-in-law", "Brother-in-law", "Wife", "Sister"),
        ("A man said to a lady, 'Your mother's husband's sister is my aunt.' How is the lady related to the man?", "Sister", "Mother", "Aunt", "Daughter"),
        ("If X is the brother of the son of Y's son, how is X related to Y?", "Grandson", "Son", "Cousin", "Brother"),
        ("A is the son of C; C and Q are sisters; Z is the mother of Q. How is A related to Z?", "Grandson", "Son", "Nephew", "Brother"),
        ("Pointing to a boy in the park, Carol said, 'His sister is the daughter of my grandfather's only son.' How is the boy related to Carol?", "Brother", "Cousin", "Uncle", "Nephew"),
        ("B is the father of Q. B has only two children. Q is the brother of R. R is the daughter of P. A is the granddaughter of P. S is the father of A. How is S related to Q?", "Brother-in-law", "Brother", "Son", "Father"),
        ("A woman introduces a man as the son of the brother of her mother. How is the man related to the woman?", "Cousin", "Nephew", "Uncle", "Brother"),
        ("Rahul's mother is the only daughter of Monika's father. How is Monika's husband related to Rahul?", "Father", "Uncle", "Grandfather", "Brother"),
        ("Pointing to a gentleman, Deepak said, 'His only brother is the father of my daughter's father.' How is the gentleman related to Deepak?", "Uncle", "Father", "Brother", "Grandfather"),
        ("If 'A + B' means A is the brother of B, 'A - B' means A is the sister of B, and 'A * B' means A is the father of B. Which of the following means that C is the son of M?", "M * C + N", "M + C * N", "M - C * N", "C * M + N"),
        ("Looking at a portrait, a woman says, 'Her mother's only daughter is my mother.' Who is in the portrait?", "The woman's mother", "The woman herself", "The woman's grandmother", "The woman's daughter"),
        ("P is the sister of D. D is married to P's friend B. B is the son of M. How is D related to M?", "Daughter-in-law (or Son-in-law)", "Daughter", "Sister", "Cousin"),
        ("Pointing to a man, a woman says, 'His mother is the wife of my father's only son.' How is the man related to the woman?", "Son", "Nephew", "Brother", "Cousin"),
        ("A is the uncle of B, who is the daughter of C. C is the sister of A. How is B related to A?", "Niece", "Nephew", "Sister", "Daughter"),
        ("If E is the daughter of A, D is the son of B, and B is married to A. What is the relation of D to E?", "Brother", "Cousin", "Uncle", "Father"),
        ("A man walking in a garden meets a boy and asks his relation. The boy replies: 'Brothers and sisters I have none, but that man's father is my father's son.' Who is the boy to the man?", "His son", "Himself", "His father", "His nephew"),
    ]
    for q, c, w1, w2, w3 in blood_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 4. Direction & Distance Sense (20 questions)
    dir_scenarios = [
        ("A person walks 5 km North, then turns right and walks 12 km. How far is he from his starting point in a straight line?", "13 km (Pythagorean triplet)", "17 km", "15 km", "11 km"),
        ("Starting from point A, Sarah walks 10 meters East, turns South and walks 6 meters, then turns West and walks 10 meters. How far and in which direction is she from A?", "6 meters South", "6 meters North", "10 meters East", "4 meters South"),
        ("At sunrise, a morning jogger observes that his shadow falls directly behind him. In which direction is he facing?", "West", "East", "North", "South"),
        ("A man walks 4 km East, turns left and walks 3 km. What is the shortest distance back to his starting point?", "5 km", "7 km", "6 km", "4 km"),
        ("If South-East becomes North, North-East becomes West, and so on. What will West become?", "South-East", "North-West", "South-West", "North-East"),
        ("A cyclist rides 8 km South, turns right and rides 6 km. How far is he from his initial location?", "10 km", "14 km", "12 km", "8 km"),
        ("David faces North. He turns 90° clockwise, then 180° counter-clockwise. Which direction is he facing now?", "West", "East", "South", "North"),
        ("At sunset, two friends stand facing each other. Alice notices that Bob's shadow falls to her right. In which direction is Alice facing?", "North", "South", "East", "West"),
        ("A drone flies 30 meters North, turns left and flies 40 meters, then turns left again and flies 30 meters. How far is it from the launch pad?", "40 meters", "30 meters", "50 meters", "70 meters"),
        ("A runner moves 15 km West, turns right and runs 8 km. What is the displacement from the starting mark?", "17 km", "23 km", "19 km", "15 km"),
        ("Facing East, a security guard turns 45° clockwise, then 90° anti-clockwise. Which direction is he facing now?", "North-East", "South-East", "North-West", "East"),
        ("Starting from home, Leo walks 20m West, turns South and walks 10m, then walks 20m East. How far is he from home?", "10 meters", "20 meters", "30 meters", "0 meters"),
        ("A delivery truck travels 12 miles South, 5 miles West, and 12 miles North. How far is it from its starting depot?", "5 miles", "12 miles", "17 miles", "7 miles"),
        ("If a clock shows 3:00, and the minute hand points North, in which direction does the hour hand point?", "East", "West", "South", "South-East"),
        ("A hiker walks 3 km North, turns right and walks 4 km, then turns right again and walks 3 km. In which direction is he from the start?", "East", "North", "South", "West"),
        ("A person walks 20m North, turns 90° left and walks 15m. How far is he from the starting point?", "25 meters", "35 meters", "20 meters", "30 meters"),
        ("In the evening just before dusk, a pole casts a shadow to its East. Where is the Sun situated?", "West", "East", "North", "South"),
        ("Walking 60m South, Kevin turns left and walks 40m, then turns left again and walks 60m. In which direction is he now from his starting position?", "East", "West", "North", "South"),
        ("A car travels 50 km East, then turns right and travels 120 km. What is the straight-line distance from the start?", "130 km", "150 km", "170 km", "110 km"),
        ("Mary walks 10m towards North, turns right and walks 10m, then turns right and walks 5m, then turns right and walks 10m. How far is she from her starting point?", "5 meters", "10 meters", "15 meters", "0 meters"),
    ]
    for q, c, w1, w2, w3 in dir_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 5. Syllogisms & Deductive Logic (20 questions)
    syl_scenarios = [
        ("Statements: All roses are flowers. All flowers are plants. Conclusion I: All roses are plants. Conclusion II: Some plants are roses.", "Both I and II follow", "Only I follows", "Only II follows", "Neither follows"),
        ("Statements: Some laptops are tablets. All tablets are computers. Conclusion: Some laptops are computers.", "Conclusion follows logically", "Conclusion does not follow", "Cannot be determined", "Both are false"),
        ("Statements: All engineers are professionals. No professionals are careless. Conclusion: No engineers are careless.", "Conclusion follows definitely", "Conclusion does not follow", "Partially true", "Contradictory"),
        ("Statements: Some birds can swim. All penguins are birds. Conclusion: All penguins can swim.", "Does not necessarily follow", "Follows definitely", "Conclusion is false", "Cannot be verified"),
        ("Statements: All metals conduct electricity. Copper is a metal. Conclusion: Copper conducts electricity.", "Follows validly", "Does not follow", "Ambiguous", "Requires more premises"),
        ("Statements: No reptiles have fur. All snakes are reptiles. Conclusion: No snakes have fur.", "Follows definitely", "Does not follow", "Partially true", "Unsound deduction"),
        ("Statements: All books have pages. This notebook has pages. Conclusion: This notebook is a book.", "Does not follow (Fallacy of the undistributed middle)", "Follows definitely", "Always true", "Factually certain"),
        ("Statements: Some cars are electric. All electric vehicles are eco-friendly. Conclusion: Some cars are eco-friendly.", "Follows logically", "Does not follow", "False conclusion", "Incomplete statement"),
        ("Statements: All poets are dreamers. Some artists are poets. Conclusion: Some artists are dreamers.", "Follows definitely", "Does not follow", "Only poets are dreamers", "Cannot be deduced"),
        ("Statements: No square is a circle. All circles are curves. Conclusion: No square is a curve.", "Does not necessarily follow", "Follows definitely", "Contradicts premises", "False deduction"),
        ("Statements: All diamonds are carbon. Some minerals are diamonds. Conclusion: Some minerals are carbon.", "Follows logically", "Does not follow", "All minerals are carbon", "None follows"),
        ("Statements: Some teachers are writers. Some writers are musicians. Conclusion: Some teachers are musicians.", "Does not necessarily follow", "Follows definitely", "Always true", "Invalid premise"),
        ("Statements: All mammals are warm-blooded. Whales are mammals. Conclusion: Whales are warm-blooded.", "Follows validly", "Does not follow", "Doubtful", "False statement"),
        ("Statements: No honest person is a fraud. Some politicians are honest. Conclusion: Some politicians are not frauds.", "Follows definitely", "Does not follow", "All politicians are honest", "Contradictory"),
        ("Statements: All stars emit light. The sun is a star. Conclusion: The sun emits light.", "Follows conclusively", "Does not follow", "Partially follows", "Invalid deduction"),
        ("Statements: Some fruits are sweet. Lemon is a fruit. Conclusion: Lemon is sweet.", "Does not follow", "Follows definitely", "Always true", "Partially follows"),
        ("Statements: All rectangles have four sides. A square is a rectangle. Conclusion: A square has four sides.", "Follows logically", "Does not follow", "False syllogism", "Invalid premise"),
        ("Statements: Every cloud has moisture. Cirrus is a cloud. Conclusion: Cirrus has moisture.", "Follows validly", "Does not follow", "Probable only", "False premise"),
        ("Statements: Some doctors are researchers. Dr. Smith is a doctor. Conclusion: Dr. Smith is a researcher.", "Does not necessarily follow", "Follows definitely", "True statement", "Guaranteed deduction"),
        ("Statements: All organic compounds contain carbon. Methane is an organic compound. Conclusion: Methane contains carbon.", "Follows conclusively", "Does not follow", "False conclusion", "Incomplete deduction"),
    ]
    for q, c, w1, w2, w3 in syl_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 6. Seating Arrangement & Order/Ranking (20 questions)
    seat_scenarios = [
        ("Five colleagues A, B, C, D, and E sit in a row facing North. C sits in the exact middle. A is to the immediate left of C. Where does A sit?", "Second from the left", "First from the left", "Fourth from the left", "Third from the left"),
        ("In a class of 45 students, Jack ranks 15th from the top. What is his rank from the bottom?", "31st (45 - 15 + 1)", "30th", "32nd", "29th"),
        ("Six friends are seated around a circular table facing the center. If Peter sits directly opposite to Mary, how many seats are between them on either side?", "2 seats", "3 seats", "1 seat", "4 seats"),
        ("In a queue, David is 8th from the front and 14th from the rear. How many people are in the queue?", "21 people (8 + 14 - 1)", "22 people", "20 people", "23 people"),
        ("A is taller than B, but shorter than C. D is taller than E, but shorter than B. Who is the tallest among them?", "C", "A", "B", "D"),
        ("In a row of 30 trees, an apple tree is 11th from the left. What is its position from the right?", "20th", "19th", "21st", "18th"),
        ("Four boxes P, Q, R, S are stacked. P is above Q, and R is below S. If S is below Q, which box is at the bottom?", "R", "S", "Q", "P"),
        ("In a sprint, Kevin finished ahead of Tom but behind Liam. Mark finished ahead of Liam. Who won the sprint?", "Mark", "Liam", "Kevin", "Tom"),
        ("Seven students P, Q, R, S, T, U, V are seated in a row. S is in the middle. How many students sit to the left of S?", "3 students", "4 students", "2 students", "1 student"),
        ("In a ranking list, Priya is 7 ranks ahead of Ashok, who ranks 17th from the top. What is Priya's rank from the top?", "10th", "24th", "9th", "11th"),
        ("Six people sit around a table. A sits between B and C. D sits opposite to A. Who sits opposite to B if E is adjacent to C?", "E (or D depending on symmetry)", "C", "D", "A"),
        ("If Anita is 9th from either end of a row of girls, how many girls are in the row?", "17 girls (9 + 9 - 1)", "18 girls", "19 girls", "16 girls"),
        ("Among five friends, E is heavier than K but lighter than M. D is lighter than K but heavier than B. Who is the second heaviest?", "E", "M", "K", "D"),
        ("A line of soldiers has 25 soldiers. Sergeant Vance is 13th from the left. Where is he relative to the center?", "He is in the exact center", "1 position to the left of center", "1 position to the right of center", "2 positions left"),
        ("In an auditorium row, Paul sits 12th from the left and Brian sits 18th from the right. If they swap seats, Paul becomes 25th from the left. How many seats are in the row?", "42 seats (25 + 18 - 1)", "43 seats", "41 seats", "40 seats"),
        ("Five cars P, Q, R, S, T are parked in a straight lane. T is parked to the left of Q. P is to the right of Q. S is to the right of P but to the left of R. Which car is in the middle?", "P", "Q", "S", "T"),
        ("In a competition, Emma scored higher than Lucas, but lower than Chloe. Ethan scored lower than Lucas. Who had the lowest score?", "Ethan", "Lucas", "Emma", "Chloe"),
        ("Eight delegates sit at a round conference table. How many distinct pairs of delegates sit directly opposite each other?", "4 pairs", "8 pairs", "2 pairs", "6 pairs"),
        ("In a class test, Ronald ranks 6th from the top and 28th from the bottom. How many students took the test?", "33 students", "34 students", "32 students", "35 students"),
        ("There are 5 books A, B, C, D, E on a table. If A is placed above B, C is placed below D, B is placed above C and D is placed above E, which book is at the very bottom?", "E", "C", "B", "A"),
    ]
    for q, c, w1, w2, w3 in seat_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 7. Odd One Out & Classification (20 questions)
    odd_scenarios = [
        ("Find the odd one out from the group: Iron, Copper, Zinc, Oxygen.", "Oxygen (Non-metal / gas)", "Iron", "Copper", "Zinc"),
        ("Choose the odd word: Triangle, Rectangle, Cylinder, Pentagon.", "Cylinder (3D shape, others are 2D polygons)", "Triangle", "Rectangle", "Pentagon"),
        ("Identify the odd one out: 27, 64, 125, 144.", "144 (Square of 12, others are perfect cubes)", "27", "64", "125"),
        ("Find the odd one out: Mercury, Venus, Moon, Mars.", "Moon (Satellite, others are planets)", "Mercury", "Venus", "Mars"),
        ("Choose the odd word: Python, Java, C++, HTML.", "HTML (Markup language, others are programming languages)", "Python", "Java", "C++"),
        ("Identify the odd one out: Paris, London, Tokyo, Sydney.", "Sydney (Not a national capital)", "Paris", "London", "Tokyo"),
        ("Find the odd one out: 13, 17, 23, 27.", "27 (Composite number, others are primes)", "13", "17", "23"),
        ("Choose the odd one out: Dollar, Euro, Yen, Gram.", "Gram (Unit of mass, others are currencies)", "Dollar", "Euro", "Yen"),
        ("Identify the odd word: Whale, Dolphin, Shark, Seal.", "Shark (Cartilaginous fish, others are marine mammals)", "Whale", "Dolphin", "Seal"),
        ("Find the odd one out: Violin, Cello, Flute, Guitar.", "Flute (Woodwind instrument, others are string instruments)", "Violin", "Cello", "Guitar"),
        ("Choose the odd pair: (2, 8), (3, 27), (4, 64), (5, 100).", "(5, 100) - Should be 125 (n^3)", "(2, 8)", "(3, 27)", "(4, 64)"),
        ("Identify the odd word: Thermometer, Barometer, Odometer, Diameter.", "Diameter (Geometric measurement, others are measuring instruments)", "Thermometer", "Barometer", "Odometer"),
        ("Find the odd one out: Eagle, Sparrow, Bat, Pigeon.", "Bat (Mammal, others are birds)", "Eagle", "Sparrow", "Pigeon"),
        ("Choose the odd one out: Apple, Orange, Banana, Potato.", "Potato (Root vegetable, others are fruits)", "Apple", "Orange", "Banana"),
        ("Identify the odd one out: Kilogram, Meter, Second, Degree.", "Degree (Derived/angular unit, others are SI base units)", "Kilogram", "Meter", "Second"),
        ("Find the odd one out: Google, Bing, Yahoo, Microsoft Windows.", "Microsoft Windows (Operating system, others are search engines)", "Google", "Bing", "Yahoo"),
        ("Choose the odd word: Retina, Cornea, Pupil, Ear canal.", "Ear canal (Part of ear, others are eye parts)", "Retina", "Cornea", "Pupil"),
        ("Identify the odd one out: 121, 144, 169, 175.", "175 (Not a perfect square)", "121", "144", "169"),
        ("Find the odd one out: Diamond, Graphite, Coal, Bronze.", "Bronze (Metal alloy, others are carbon allotropes/forms)", "Diamond", "Graphite", "Coal"),
        ("Choose the odd one out: Linux, Android, iOS, Oracle.", "Oracle (Database/software company, others are operating systems)", "Linux", "Android", "iOS"),
    ]
    for q, c, w1, w2, w3 in odd_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 8. Critical Thinking & Assumptions (20 questions)
    crit_scenarios = [
        ("Statement: 'The city council urges all residents to install water-saving showerheads.' What is an implicit assumption?", "Water conservation is necessary in the municipality", "All existing showerheads are currently broken", "Residents will receive fines if they decline", "Water prices will double tomorrow"),
        ("Statement: 'Enrolling in our accelerated coding boot camp guarantees an interview with top software firms.' Assumption:", "Top software firms hire talent from coding boot camps", "College degrees are now legally banned in tech", "Every candidate is already an experienced programmer", "Boot camp tuition is completely free"),
        ("Argument: 'Electric scooters should be banned on walkways because they cause pedestrian collisions.' What strengthens this argument?", "Hospital statistics report a 40% surge in walkway accidents involving electric scooters", "Scooters reduce automobile traffic", "Electric scooters are zero-emission vehicles", "Young riders enjoy riding scooters"),
        ("Statement: 'Apply before December 31 to qualify for early-bird university tuition waivers.' Assumption:", "Some applicants prefer discounts on tuition fees", "The university will close admissions on December 31", "No one will apply after December 31", "The tuition waiver is offered to all applicants automatically"),
        ("Argument: 'Remote work reduces company overhead by minimizing leased office space.' What assumption underlies this claim?", "Physical office lease is a significant company expense", "All employees work better from home", "Remote employees require zero technology support", "Clients never visit corporate headquarters"),
        ("Statement: 'Eat whole grains daily for enhanced digestive health.' What assumption is valid?", "Dietary whole grains contribute positively to digestion", "Whole grains cure all illnesses", "Vegetables have zero dietary value", "People dislike whole grains"),
        ("Statement: 'Subscribe to our annual cloud backup to safeguard your enterprise data from ransomware.' Assumption:", "Enterprise data is vulnerable to ransomware and backups mitigate loss", "Cloud backups make computers run faster", "Ransomware targets only cloud storage", "Subscribers never experience cyber threats"),
        ("Argument: 'Bilingual education in primary schools enhances overall cognitive agility.' What evidence would strengthen this?", "Neuroscience research showing higher executive function scores in bilingual children", "Bilingual programs require additional specialized instructors", "Many parents speak only one language", "Schools have limited foreign language resources"),
        ("Statement: 'Please silence your mobile phones during the symphony concert.' Assumption:", "Mobile phone ringtones disrupt musical performances", "Audience members cannot read musical notes", "The concert hall has no cellular signal", "Musicians perform without scores"),
        ("Statement: 'Drink at least 2 liters of water daily to maintain cellular hydration.' Assumption:", "Hydration requires consistent fluid intake throughout the day", "Water is the only consumable liquid", "Drinking 2 liters cures viral infections", "Humans cannot absorb water from food"),
        ("Argument: 'Solar panel subsidies should be increased to meet national clean energy targets.' What assumption is made?", "Subsidies make solar adoption more financially accessible to citizens", "Solar panels generate energy during nighttime", "Fossil fuels have become entirely free", "Wind turbines are ineffective"),
        ("Statement: 'Do not lean against the automatic subway doors.' Assumption:", "Leaning on moving transit doors poses safety risks", "Subway doors never open at stations", "Subway trains travel faster without passengers", "Passengers prefer standing near the train operator"),
        ("Statement: 'Read the instructions leaflet carefully before assembling the furniture.' Assumption:", "Assembly instructions guide correct and safe installation", "The furniture will break if instructions are read", "Anyone can assemble furniture without tools", "Instructions are written in multiple languages"),
        ("Argument: 'Introducing mandatory physical education in high school curricula reduces adolescent obesity rates.' What strengthens this?", "Data demonstrating lower BMI among students engaging in daily school sports", "High schools have sports fields", "Sports uniforms are costly", "Academic exams cause physical exhaustion"),
        ("Statement: 'Switch off the engine at red traffic lights lasting longer than 40 seconds.' Assumption:", "Switching off engines during prolonged stops conserves fuel and reduces emissions", "Engines cannot restart after being switched off", "Traffic lights remain red for hours", "Automobiles do not have brakes"),
        ("Statement: 'Check expiration dates on packaged medicines prior to consumption.' Assumption:", "Medicines past their expiration date may lose efficacy or become harmful", "All medicines expire within one week", "Expired medicines change color immediately", "Pharmacies never sell unexpired items"),
        ("Argument: 'Public libraries should expand digital audiobook catalogs.' Assumption:", "There is significant public demand for digital audiobooks", "Paper books should be eliminated immediately", "Audiobooks require no electricity", "Library staff do not support digital resources"),
        ("Statement: 'Always wear a seatbelt, even on short vehicular journeys.' Assumption:", "Vehicular collisions can occur regardless of travel distance", "Short trips are completely risk-free", "Seatbelts are only useful on highways", "Modern cars have no airbags"),
        ("Statement: 'Install anti-virus software to protect your workstation against phishing and malware.' Assumption:", "Workstations connected to networks face threats from malicious software", "Antivirus software eliminates the need for strong passwords", "Malware targets only smartphones", "Anti-virus programs generate computer viruses"),
        ("Argument: 'Universal preschool education yields substantial long-term economic returns for society.' What strengthens this premise?", "Longitudinal studies showing preschool attendees attain higher graduation and employment rates", "Preschool requires trained early childhood educators", "Young children enjoy creative play", "Preschool hours are shorter than elementary school"),
    ]
    for q, c, w1, w2, w3 in crit_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 9. Clocks, Calendars & Angles (20 questions)
    clock_scenarios = [
        ("What is the angle between the hour hand and the minute hand of a clock at 3:00?", "90°", "80°", "100°", "85°"),
        ("What is the angle between the hour hand and minute hand at 3:30?", "75° (Angle = |30*H - 5.5*M|)", "90°", "70°", "80°"),
        ("At what time between 4 and 5 o'clock will the hands of a clock be together (overlap)?", "21 9/11 minutes past 4", "20 minutes past 4", "22 minutes past 4", "21 5/11 minutes past 4"),
        ("How many times do the hands of a clock coincide in a 24-hour day?", "22 times", "24 times", "20 times", "23 times"),
        ("How many times in a day (24 hours) are the hands of a clock at right angles (90°)?", "44 times", "48 times", "24 times", "22 times"),
        ("If today is Wednesday, what day of the week will it be after 64 days? (64 mod 7 = 1)", "Thursday", "Wednesday", "Friday", "Tuesday"),
        ("Which of the following years was a leap year?", "2024", "2021", "2022", "2023"),
        ("Is the century year 1900 a leap year?", "No (Not divisible by 400)", "Yes", "Partially", "Only in the Julian calendar"),
        ("What is the angle between the hands of a clock at 6:00?", "180°", "170°", "190°", "165°"),
        ("If January 1, 2024 was a Monday, what day was January 1, 2025? (2024 was a leap year, 366 days = +2 odd days)", "Wednesday", "Tuesday", "Thursday", "Monday"),
        ("What is the angle between the hands of a clock at 8:20?", "130°", "120°", "140°", "125°"),
        ("How many leap years occur in a period of 100 consecutive normal years (excluding 400th century year)?", "24 leap years", "25 leap years", "20 leap years", "26 leap years"),
        ("If the 5th of a month falls on a Sunday, what day of the week will the 26th fall on? (26 - 5 = 21 days = 3 weeks)", "Sunday", "Monday", "Saturday", "Friday"),
        ("What is the angle between clock hands at 12:15?", "82.5°", "90°", "85°", "77.5°"),
        ("How many odd days are there in a standard non-leap year of 365 days? (365 mod 7)", "1 odd day", "2 odd days", "0 odd days", "3 odd days"),
        ("How many odd days are in a leap year of 366 days? (366 mod 7)", "2 odd days", "1 odd day", "0 odd days", "3 odd days"),
        ("At what angle are the hands of a clock at 9:00?", "90°", "80°", "100°", "75°"),
        ("A watch gains 5 seconds every 3 minutes. If it was set right at 7:00 AM, how much will it gain in 6 hours?", "10 minutes", "12 minutes", "8 minutes", "15 minutes"),
        ("What was the day of the week on 15th August 1947?", "Friday", "Thursday", "Saturday", "Sunday"),
        ("How many times do the hands of a clock point in opposite directions (180°) in 12 hours?", "11 times", "12 times", "10 times", "13 times"),
    ]
    for q, c, w1, w2, w3 in clock_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 10. Venn Diagrams, Sets & Analytical Logic (20 questions)
    venn_scenarios = [
        ("In a class of 50 students, 30 play soccer, 25 play basketball, and 10 play both sports. How many students play neither sport?", "5 students (50 - (30+25-10))", "10 students", "0 students", "15 students"),
        ("In a group of 100 tourists, 70 speak English, 45 speak French, and 25 speak both. How many speak only English?", "45 tourists (70 - 25)", "50 tourists", "40 tourists", "35 tourists"),
        ("Which geometric diagram best represents the relationship: 'Mammals, Dogs, Pets'?", "Intersecting circles with Dogs fully inside Mammals and overlapping Pets", "Three disjoint circles", "Three concentric circles", "Two circles inside one large circle"),
        ("Out of 60 software developers, 40 know Python and 30 know JavaScript. If 5 know neither, how many know both languages?", "15 developers (40+30 - (60-5))", "20 developers", "10 developers", "25 developers"),
        ("Which diagram best depicts: 'Vehicles, Cars, Bicycles'?", "A large circle (Vehicles) containing two separate circles (Cars and Bicycles)", "Three overlapping circles", "Three mutually exclusive circles", "Two concentric circles outside one circle"),
        ("In an office of 80 employees, 50 drink coffee, 40 drink tea, and every employee drinks at least one of the two. How many drink both?", "10 employees (50+40 - 80)", "15 employees", "5 employees", "20 employees"),
        ("Which representation illustrates: 'Doctors, Musicians, Men'?", "Three mutually intersecting circles", "Two circles enclosed in one", "Three disconnected circles", "Concentric circles"),
        ("If set A has 5 elements and set B has 7 elements. What is the minimum possible number of elements in (A union B)?", "7 elements (when A is subset of B)", "5 elements", "12 elements", "0 elements"),
        ("What is the maximum number of elements in (A union B) if |A| = 5 and |B| = 7?", "12 elements (when A and B are disjoint)", "10 elements", "7 elements", "14 elements"),
        ("In a survey of 200 college students, 120 like sci-fi movies, 90 like comedy, and 40 like both. How many like neither genre?", "30 students (200 - (120+90-40))", "40 students", "20 students", "50 students"),
        ("Which diagram represents the relation: 'Animals, Carnivores, Lions'?", "A circle for Lions inside Carnivores, both inside Animals", "Three separate circles", "Two intersecting circles inside one", "Three overlapping circles"),
        ("In a sports club of 90 members, 55 play tennis and 45 play badminton. If 15 play both, how many play only badminton?", "30 members (45 - 15)", "40 members", "25 members", "35 members"),
        ("Which set best describes: 'Fruit, Apple, Potato'?", "A circle for Apple inside Fruit, and an independent circle for Potato", "Three intersecting circles", "Apple inside Potato inside Fruit", "Three separate circles"),
        ("If set A and set B are disjoint sets, what is their intersection (A ∩ B)?", "Empty set (∅)", "Set A", "Set B", "Universal set"),
        ("In an election survey of 500 voters, 280 favor Proposition A, 220 favor Proposition B, and 80 favor both. How many favor neither proposition?", "80 voters (500 - (280+220-80))", "100 voters", "60 voters", "120 voters"),
        ("Which diagram best represents: 'Teachers, Writers, Researchers'?", "Three mutually intersecting circles with common region", "Three concentric circles", "Two separate circles inside one", "Three disjoint circles"),
        ("In an orchestra of 40 musicians, 24 play violin, 18 play viola, and 8 play both. How many play neither instrument?", "6 musicians (40 - (24+18-8))", "8 musicians", "4 musicians", "10 musicians"),
        ("Which diagram depicts: 'Atmosphere, Nitrogen, Oxygen'?", "A large circle (Atmosphere) containing two disjoint circles (Nitrogen and Oxygen)", "Three concentric circles", "Three intersecting circles", "Two circles outside one"),
        ("In a group of 30 researchers, 18 publish in AI, 14 publish in Robotics, and 6 publish in both. How many publish in only AI?", "12 researchers (18 - 6)", "14 researchers", "10 researchers", "8 researchers"),
        ("If set X is a proper subset of set Y, which statement is always true?", "All elements of X are in Y, but Y has at least one element not in X", "X and Y are identical", "X has more elements than Y", "X and Y have no common elements"),
    ]
    for q, c, w1, w2, w3 in venn_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    return questions
