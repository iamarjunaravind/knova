# 200 Quality Numerical Ability Questions with detailed mathematical scenarios

def get_numerical_questions():
    questions = []
    
    # 1. Percentages & Discounts (20 questions)
    pct_scenarios = [
        ("A smartphone originally priced at $800 is offered at a 15% promotional discount. What is the final price?", "$680", "$690", "$720", "$650"),
        ("A laptop's cost increased from $500 to $650. What is the percentage increase in its price?", "30%", "25%", "35%", "20%"),
        ("If 25% of a number is 45, what is 40% of the same number?", "72", "65", "80", "58"),
        ("A retailer offers two successive discounts of 20% and 10% on a jacket with a list price of $200. What is the final sale price?", "$144", "$140", "$150", "$160"),
        ("In an examination, a student scored 360 marks out of 450. What percentage did the student achieve?", "80%", "78%", "82%", "75%"),
        ("If the price of petrol increases by 25%, by what percentage must a driver reduce consumption to keep the expenditure unchanged?", "20%", "25%", "15%", "18%"),
        ("A real estate agent sells an apartment for $250,000 and earns a 3.5% commission. How much commission is received?", "$8,750", "$7,500", "$9,250", "$8,500"),
        ("An item bought for $120 is sold for $150. What is the profit percentage?", "25%", "20%", "30%", "15%"),
        ("A merchant sells a watch for $180, incurring a 10% loss. What was the original cost price?", "$200", "$198", "$210", "$190"),
        ("The population of a city grew by 5% in year 1 and 10% in year 2. What is the overall percentage growth over the two years?", "15.5%", "15%", "16%", "14.5%"),
        ("A trader marks his goods 40% above cost price and then offers a 20% discount. What is his net profit percentage?", "12%", "20%", "15%", "10%"),
        ("If 30% of A equals 45% of B, what is the ratio of A to B?", "3:2", "2:3", "9:4", "4:3"),
        ("In a survey of 1,200 people, 65% preferred digital textbooks. How many people preferred digital textbooks?", "780", "720", "800", "750"),
        ("A solar inverter was sold for $540 at a 20% profit. What was its cost price?", "$450", "$432", "$460", "$480"),
        ("After spending 35% of his salary on rent and 25% on food, a worker saves $800. What is his total monthly salary?", "$2,000", "$1,800", "$2,200", "$2,500"),
        ("A company's quarterly revenue rose from $1.2 million to $1.5 million. What is the growth percentage?", "25%", "20%", "30%", "22.5%"),
        ("If a bookstore offers 'Buy 3, Get 1 Free', what is the effective percentage discount?", "25%", "33.3%", "20%", "30%"),
        ("A shopkeeper sells two items for $990 each, making a 10% gain on one and a 10% loss on the other. What is the net outcome?", "1% loss", "No profit no loss", "1% gain", "2% loss"),
        ("What single discount is equivalent to two successive discounts of 15% and 20%?", "32%", "35%", "30%", "28%"),
        ("A candidate secures 42% marks in a test and fails by 18 marks. The passing threshold is 48%. What are the maximum marks?", "300", "250", "350", "400"),
    ]
    for q, c, w1, w2, w3 in pct_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 2. Ratios, Proportions & Partnerships (20 questions)
    ratio_scenarios = [
        ("Two numbers are in the ratio 4:5. If their sum is 135, what is the smaller number?", "60", "75", "55", "65"),
        ("If a:b = 2:3 and b:c = 4:5, what is the compound ratio a:b:c?", "8:12:15", "6:9:15", "8:10:15", "2:3:5"),
        ("Divide $1,500 among A, B, and C in the ratio 2:3:5. How much does B receive?", "$450", "$300", "$750", "$500"),
        ("A mixture contains milk and water in the ratio 7:3. If the total volume is 50 liters, how much water is in the mixture?", "15 liters", "35 liters", "20 liters", "10 liters"),
        ("In an office, the ratio of male to female employees is 5:6. If there are 36 female employees, how many male employees are there?", "30", "25", "35", "28"),
        ("The ratio of two numbers is 3:4. If 5 is added to each number, the new ratio becomes 4:5. What are the original numbers?", "15 and 20", "12 and 16", "9 and 12", "18 and 24"),
        ("Three partners invest $10,000, $15,000, and $25,000 in a startup. If the annual profit is $10,000, what is the share of the third partner?", "$5,000", "$3,000", "$2,000", "$4,000"),
        ("A 60-liter solution has alcohol and water in the ratio 2:1. How much water must be added to make the ratio 1:1?", "20 liters", "10 liters", "15 liters", "25 liters"),
        ("If 4 men or 6 women can reap a field in 20 days, how many days will 6 men and 11 women take?", "7 days", "8 days", "9 days", "6 days"),
        ("The ages of two brothers are in the ratio 5:7. Eight years ago, their ages were in the ratio 3:5. What are their present ages?", "20 and 28", "15 and 21", "25 and 35", "10 and 14"),
        ("The ratio of length to width of a soccer field is 3:2. If the perimeter is 300 meters, what is the length?", "90 meters", "60 meters", "100 meters", "120 meters"),
        ("If x:y = 3:4, what is the value of (4x + 3y) / (6x - 2y)?", "12/5", "24/10", "12/7", "8/3"),
        ("A bronze alloy is composed of copper and tin in the ratio 9:1. How much tin is present in a 50 kg bronze statue?", "5 kg", "4.5 kg", "6 kg", "5.5 kg"),
        ("The speeds of three cars are in the ratio 2:3:4. What is the ratio of time taken by them to travel the same distance?", "6:4:3", "4:3:2", "2:3:4", "3:4:6"),
        ("Two containers have milk and water mixtures in ratios 3:2 and 4:1. If equal volumes are mixed, what is the ratio of milk to water in the new mixture?", "7:3", "3:1", "11:9", "5:3"),
        ("If 15% of x is equal to 20% of y, what is x:y?", "4:3", "3:4", "5:4", "1:2"),
        ("An alloy contains zinc, copper, and tin in the ratio 2:3:5. How much copper is in a 120-gram sample?", "36 grams", "24 grams", "60 grams", "48 grams"),
        ("If a recipe requires flour and sugar in the ratio 5:2, how much sugar is needed for 750 grams of flour?", "300 grams", "250 grams", "350 grams", "200 grams"),
        ("The ratio of incomes of A and B is 5:4 and their expenditures are in the ratio 3:2. If each saves $1,600, what is A's income?", "$4,000", "$3,200", "$4,800", "$5,000"),
        ("In what ratio must water be mixed with milk costing $60/liter to produce a mixture worth $45/liter?", "1:3", "1:4", "2:3", "1:2"),
    ]
    for q, c, w1, w2, w3 in ratio_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 3. Simple & Compound Interest (20 questions)
    interest_scenarios = [
        ("Calculate the simple interest on $5,000 invested at 6% per annum for 3 years.", "$900", "$950", "$850", "$1,000"),
        ("A sum of $2,000 earns $360 simple interest in 3 years. What is the annual interest rate?", "6%", "5%", "7%", "8%"),
        ("In how many years will an investment double itself at an 8% simple interest rate per annum?", "12.5 years", "10 years", "15 years", "11.2 years"),
        ("Find the compound interest on $4,000 at 10% per annum compounded annually for 2 years.", "$840", "$800", "$880", "$820"),
        ("What is the difference between simple interest and compound interest on $10,000 at 5% per annum for 2 years?", "$25", "$20", "$30", "$15"),
        ("A sum of money invested at compound interest doubles itself in 4 years. In how many years will it become 8 times its initial value?", "12 years", "16 years", "8 years", "10 years"),
        ("What principal will yield $1,200 simple interest at 5% per annum in 4 years?", "$6,000", "$5,500", "$6,500", "$7,000"),
        ("Calculate the compound amount on $8,000 for 1 year at 12% per annum compounded semi-annually.", "$9,009.60", "$8,960.00", "$9,050.00", "$8,920.00"),
        ("A borrower pays $720 in interest after borrowing $3,000 for 4 years. What was the annual simple interest rate?", "6%", "5.5%", "6.5%", "7%"),
        ("If a principal amounts to $2,420 in 2 years at 10% compound interest per annum, what is the principal?", "$2,000", "$2,100", "$1,950", "$2,050"),
        ("What is the effective annual rate for a nominal rate of 8% compounded quarterly?", "8.24%", "8.16%", "8.08%", "8.32%"),
        ("At what simple interest rate will $1,500 accumulate to $2,040 in 3 years?", "12%", "10%", "11%", "13%"),
        ("Find the compound interest on $5,000 for 3 years at 10% per annum compounded annually.", "$1,655", "$1,500", "$1,720", "$1,600"),
        ("If the difference between CI and SI on a sum for 2 years at 4% per annum is $8, what is the sum?", "$5,000", "$4,500", "$6,000", "$5,500"),
        ("How much interest is earned on $12,000 at 7.5% simple interest over 8 months?", "$600", "$720", "$550", "$650"),
        ("A certificate of deposit yields a compound interest of 6% compounded monthly. What is the formula base for 1 month?", "1 + 0.06/12", "1 + 0.06", "1 + 0.06*12", "1 + 0.06/365"),
        ("A loan of $15,000 is repaid with $19,500 after 3 years. What simple interest rate was applied?", "10%", "9%", "11%", "8.5%"),
        ("If a sum triples at simple interest in 10 years, what is the annual interest rate?", "20%", "15%", "25%", "30%"),
        ("Find the compound amount of $2,500 invested for 2 years at 8% per annum compounded annually.", "$2,916", "$2,900", "$2,850", "$2,940"),
        ("In how many years will $800 amount to $1,000 at 5% simple interest?", "5 years", "4 years", "6 years", "4.5 years"),
    ]
    for q, c, w1, w2, w3 in interest_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 4. Time, Work & Pipes (20 questions)
    work_scenarios = [
        ("A can complete a task in 12 days and B can do it in 24 days. Working together, how many days will they take?", "8 days", "9 days", "7 days", "10 days"),
        ("Pipe A fills a reservoir in 6 hours, and Pipe B fills it in 8 hours. Working together, how long will they take?", "3 hours 26 minutes", "3 hours 45 minutes", "4 hours", "3 hours 10 minutes"),
        ("Pipe A fills a tank in 10 hours while Pipe B empties it in 15 hours. How long will it take to fill the tank if both are opened?", "30 hours", "25 hours", "20 hours", "35 hours"),
        ("12 builders can construct a wall in 8 days. How many builders are needed to construct the same wall in 6 days?", "16 builders", "14 builders", "18 builders", "15 builders"),
        ("A is twice as efficient as B. If A and B together can complete a project in 14 days, in how many days can A complete it alone?", "21 days", "28 days", "18 days", "24 days"),
        ("A, B, and C can complete a job in 6, 12, and 24 days respectively. How many days will they take working together?", "3.43 days (24/7 days)", "4 days", "3.2 days", "3.8 days"),
        ("A contractor undertakes to complete a road project in 40 days and employs 25 men. After 24 days, only 1/3 of the work is done. How many extra men must he hire to finish on time?", "25 extra men", "20 extra men", "30 extra men", "15 extra men"),
        ("Two taps can fill a tub in 15 and 20 minutes respectively. A drain can empty it in 30 minutes. If all are open, how long does filling take?", "12 minutes", "10 minutes", "14 minutes", "15 minutes"),
        ("A and B can do a piece of work in 18 days; B and C in 24 days; A and C in 36 days. In how many days can A, B, and C finish it together?", "16 days", "18 days", "14 days", "20 days"),
        ("A can do a job in 20 days. After working for 5 days, A leaves, and B finishes the remaining work in 15 days. How many days would B take to do the whole job alone?", "20 days", "25 days", "18 days", "22 days"),
        ("A pump can fill a tank in 2 hours. Because of a leak, it took 2.5 hours to fill. How long will the leak take to empty the full tank?", "10 hours", "8 hours", "12 hours", "9 hours"),
        ("8 workers can assemble 40 computers in 5 days. How many computers can 12 workers assemble in 8 days?", "96 computers", "80 computers", "100 computers", "90 computers"),
        ("X is three times as fast as Y and is able to finish a job in 40 days less than Y. In how many days can they complete it together?", "15 days", "18 days", "12 days", "20 days"),
        ("A tap can fill an overhead tank in 4 hours. A second tap can empty it in 6 hours. If both taps are left open, how many hours will it take to fill the tank?", "12 hours", "10 hours", "14 hours", "8 hours"),
        ("If 5 men or 9 women can do a piece of work in 19 days, in how many days will 3 men and 6 women finish the work?", "15 days", "14 days", "16 days", "18 days"),
        ("A can complete a project in 10 days, B in 15 days, and C in 20 days. They were paid $650 in total. What is C's share of the wages?", "$150", "$200", "$300", "$100"),
        ("A and B can complete a task in 30 days. They work together for 20 days, after which B leaves. A completes the remainder in 20 days. How many days would A take alone?", "60 days", "50 days", "70 days", "45 days"),
        ("Three pipes A, B, and C can fill a tank in 6 hours. After 2 hours, C is closed, and A and B fill the rest in 7 hours. How many hours would C take alone to fill the tank?", "14 hours", "12 hours", "16 hours", "10 hours"),
        ("Worker A takes 6 hours to paint a room, while Worker B takes 4 hours. If they paint together, how long will it take?", "2.4 hours (2 hours 24 mins)", "2.5 hours", "3.0 hours", "2.2 hours"),
        ("If 10 machines produce 1,000 items in 5 hours, how many items can 6 machines produce in 8 hours?", "960 items", "800 items", "900 items", "1,020 items"),
    ]
    for q, c, w1, w2, w3 in work_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 5. Speed, Distance & Trains (20 questions)
    speed_scenarios = [
        ("A train travels at 72 km/h. How many meters does it cover in 1 second?", "20 meters", "18 meters", "22 meters", "25 meters"),
        ("A 150-meter-long train crosses a signal post in 10 seconds. What is the speed of the train in km/h?", "54 km/h", "60 km/h", "48 km/h", "72 km/h"),
        ("A car covers 180 km in 3 hours. If it increases its speed by 15 km/h, how much time will it take to cover 225 km?", "3 hours", "3.5 hours", "2.5 hours", "4 hours"),
        ("A commuter drives to work at 40 km/h and returns along the same route at 60 km/h. What is the average speed for the round trip?", "48 km/h", "50 km/h", "45 km/h", "52 km/h"),
        ("A train 240 meters long passes a platform 160 meters long in 20 seconds. What is the train's speed in km/h?", "72 km/h", "64 km/h", "80 km/h", "70 km/h"),
        ("Two trains 120m and 180m long are moving in opposite directions at 50 km/h and 40 km/h. How long will they take to cross each other?", "12 seconds", "10 seconds", "15 seconds", "8 seconds"),
        ("A boat's speed in still water is 15 km/h, and the stream's velocity is 3 km/h. What is the downstream speed of the boat?", "18 km/h", "12 km/h", "15 km/h", "20 km/h"),
        ("A boat travels 24 km downstream in 2 hours and takes 3 hours to return upstream. What is the speed of the current?", "2 km/h", "3 km/h", "1.5 km/h", "2.5 km/h"),
        ("Walking at 4 km/h, a student reaches school 5 minutes late. Walking at 5 km/h, he reaches 5 minutes early. What is the distance to school?", "3.33 km (10/3 km)", "4.0 km", "2.5 km", "3.0 km"),
        ("A cyclist covers a 750m distance in 2 minutes 30 seconds. What is his speed in km/h?", "18 km/h", "15 km/h", "20 km/h", "16 km/h"),
        ("Two cyclists leave the same point at the same time in opposite directions at 14 km/h and 16 km/h. How far apart will they be after 3 hours?", "90 km", "80 km", "100 km", "75 km"),
        ("A runner completes a 400-meter lap in 48 seconds. What is his speed in meters per second?", "8.33 m/s", "8.00 m/s", "8.50 m/s", "7.80 m/s"),
        ("How many minutes does an airplane take to fly 600 miles at an average cruise speed of 450 mph?", "80 minutes", "75 minutes", "90 minutes", "85 minutes"),
        ("A vehicle covers the first half of a distance at 30 mph and the second half at 70 mph. What is its harmonic average speed?", "42 mph", "50 mph", "45 mph", "40 mph"),
        ("Two cities are 350 km apart. Car A leaves city 1 at 40 km/h and Car B leaves city 2 toward city 1 at 30 km/h. After how many hours will they meet?", "5 hours", "6 hours", "4.5 hours", "5.5 hours"),
        ("A passenger on a train moving at 60 km/h observes that a goods train moving in the opposite direction takes 9 seconds to pass him. If the goods train is 250m long, what is its speed?", "40 km/h", "45 km/h", "35 km/h", "50 km/h"),
        ("A motorboat takes 4 hours to travel 48 km upstream. If the stream flows at 2 km/h, what is the boat's speed in still water?", "14 km/h", "12 km/h", "16 km/h", "10 km/h"),
        ("If an athlete runs at 12 km/h instead of 10 km/h, he covers 10 km more in the same duration. What was the actual distance covered at 10 km/h?", "50 km", "40 km", "60 km", "45 km"),
        ("A 300-meter freight train passes a tunnel of length 500 meters at a speed of 90 km/h. How many seconds does it take to fully cross the tunnel?", "32 seconds", "28 seconds", "35 seconds", "30 seconds"),
        ("A delivery van departs at 8:00 AM traveling at 50 km/h. Another van leaves the same point at 9:00 AM at 75 km/h in the same direction. At what time will the second van overtake the first?", "11:00 AM", "11:30 AM", "10:30 AM", "12:00 PM"),
    ]
    for q, c, w1, w2, w3 in speed_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 6. Averages, Ages & Statistics (20 questions)
    avg_scenarios = [
        ("The average of five consecutive integers is 24. What is the largest of these integers?", "26", "25", "27", "28"),
        ("The average weight of 8 students increases by 1.5 kg when a student weighing 50 kg is replaced. What is the weight of the new student?", "62 kg", "60 kg", "64 kg", "58 kg"),
        ("The average score of 20 boys is 75 and 30 girls is 85. What is the combined average score of the entire class of 50 students?", "81", "80", "82", "79"),
        ("The average of 6 numbers is 30. If the average of the first 4 is 25 and that of the last 3 is 35, what is the 4th number?", "25", "20", "30", "35"),
        ("A cricketer's batting average over 10 innings is 32. How many runs must he score in the 11th inning to raise his average to 36?", "76 runs", "72 runs", "80 runs", "70 runs"),
        ("The ratio of ages of father and son is 7:3. If the sum of their ages is 60 years, what is the age of the father?", "42 years", "40 years", "45 years", "38 years"),
        ("Five years ago, the average age of A and B was 15 years. With C joining them now, the average age becomes 20 years. How old is C?", "20 years", "18 years", "22 years", "25 years"),
        ("Find the median of the dataset: 12, 7, 19, 25, 4, 18, 11.", "12", "14", "11", "18"),
        ("What is the mode of the following set: 3, 5, 7, 5, 9, 11, 5, 8, 7?", "5", "7", "8", "3"),
        ("The average temperature of Monday, Tuesday, and Wednesday was 35°C. Tuesday, Wednesday, and Thursday was 36°C. If Thursday was 38°C, what was Monday's temperature?", "35°C", "34°C", "36°C", "37°C"),
        ("The mean of 100 observations was calculated as 40. It was later found that an observation of 53 was misread as 83. What is the corrected mean?", "39.7", "39.5", "40.3", "40.5"),
        ("A father is currently 3 times as old as his son. In 12 years, he will be twice as old as his son. What is the son's present age?", "12 years", "10 years", "14 years", "15 years"),
        ("The average age of a family of 5 members is 28 years. If the youngest member is 8 years old, what was the average age of the family just before the birth of the youngest?", "25 years", "24 years", "26 years", "20 years"),
        ("The average of seven numbers is 18. If one number is excluded, the average of the remaining numbers becomes 16. What was the excluded number?", "30", "28", "32", "26"),
        ("What is the range of the numbers: 14, 28, 9, 35, 42, 17, 21?", "33", "35", "30", "28"),
        ("In a company of 60 employees, the average monthly salary is $3,500. If the executive team of 10 earns an average of $6,000, what is the average salary of the other 50 workers?", "$3,000", "$2,800", "$3,200", "$2,900"),
        ("The average of 5 results is 46 and that of the first 4 is 45. What is the fifth result?", "50", "48", "52", "49"),
        ("A student needs an average of 80% across 4 exams to earn an 'A'. His scores on the first 3 exams are 74%, 82%, and 78%. What must he score on the 4th exam?", "86%", "84%", "88%", "82%"),
        ("The variance of a dataset is 49. What is its standard deviation?", "7", "14", "24.5", "4.9"),
        ("The average age of 24 students and their teacher is 15 years. When the teacher's age is excluded, the average age decreases by 1 year. How old is the teacher?", "39 years", "38 years", "40 years", "35 years"),
    ]
    for q, c, w1, w2, w3 in avg_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 7. Algebra & Polynomials (20 questions)
    alg_scenarios = [
        ("Solve for x: 3x + 7 = 28.", "7", "6", "8", "9"),
        ("If x + y = 15 and x - y = 5, what is the value of x * y?", "50", "45", "55", "60"),
        ("What are the roots of the quadratic equation x^2 - 7x + 12 = 0?", "3 and 4", "2 and 6", "-3 and -4", "1 and 12"),
        ("Expand the algebraic identity: (2a + 3b)^2.", "4a^2 + 12ab + 9b^2", "4a^2 + 6ab + 9b^2", "4a^2 + 9b^2", "2a^2 + 12ab + 3b^2"),
        ("If 2^(x+3) = 64, what is the value of x?", "3", "4", "2", "5"),
        ("What is the value of (a^3 - b^3) if a = 5 and b = 3?", "98", "92", "104", "88"),
        ("Factorize: x^2 - 16.", "(x - 4)(x + 4)", "(x - 4)^2", "(x + 4)^2", "(x - 8)(x + 2)"),
        ("If 5x - 3y = 11 and 2x + 3y = 17, what is the value of x?", "4", "3", "5", "2"),
        ("Simplify: (x^4 * x^7) / x^5.", "x^6", "x^5", "x^7", "x^8"),
        ("If (x + 1/x) = 4, find the value of (x^2 + 1/x^2).", "14", "16", "12", "18"),
        ("What is the slope (gradient) of the straight line 3x - 4y + 8 = 0?", "3/4", "-3/4", "4/3", "-4/3"),
        ("For what value of k will the equation 2x^2 + kx + 8 = 0 have equal roots?", "k = ±8", "k = ±4", "k = ±16", "k = ±6"),
        ("If log10(x) = 3, what is the value of x?", "1,000", "100", "10,000", "30"),
        ("Evaluate: 2^0 + 3^0 + 4^0.", "3", "0", "9", "1"),
        ("If x = 2 and y = -3, evaluate 3x^2 - 2xy + y^2.", "33", "27", "21", "30"),
        ("Solve for x: (2x - 3)/4 = 3.", "7.5 (15/2)", "6", "8", "9"),
        ("What is the y-intercept of the line y = 5x - 7?", "-7", "5", "7", "-5"),
        ("If a/b = 4/3, what is (3a + 2b) / (3a - 2b)?", "3", "2", "4", "5"),
        ("Find the discriminant of the quadratic equation 3x^2 - 5x + 2 = 0.", "1", "49", "-1", "25"),
        ("If 3^(2x - 1) = 27, what is the value of x?", "2", "3", "1.5", "2.5"),
    ]
    for q, c, w1, w2, w3 in alg_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 8. Geometry & Mensuration (20 questions)
    geo_scenarios = [
        ("What is the area of a circle with a radius of 7 cm? (Use π = 22/7)", "154 sq. cm", "144 sq. cm", "160 sq. cm", "132 sq. cm"),
        ("In a right-angled triangle, the legs are 6 cm and 8 cm. What is the length of the hypotenuse?", "10 cm", "12 cm", "9 cm", "14 cm"),
        ("What is the sum of the interior angles of a regular hexagon (6-sided polygon)?", "720°", "540°", "900°", "360°"),
        ("Calculate the volume of a cylinder with radius 3 m and height 7 m. (Use π = 22/7)", "198 cubic meters", "180 cubic meters", "210 cubic meters", "190 cubic meters"),
        ("The perimeter of a square is 48 cm. What is its area?", "144 sq. cm", "120 sq. cm", "160 sq. cm", "96 sq. cm"),
        ("What is the volume of a sphere of radius 3 cm? (Volume = 4/3 * π * r^3)", "36π cubic cm", "27π cubic cm", "48π cubic cm", "18π cubic cm"),
        ("If the diagonal of a square is 10 cm, what is the area of the square?", "50 sq. cm", "100 sq. cm", "25 sq. cm", "75 sq. cm"),
        ("Two parallel lines are intersected by a transversal. If one interior angle is 75°, what is its alternate interior angle?", "75°", "105°", "15°", "90°"),
        ("What is the total surface area of a cube with edge length 5 cm?", "150 sq. cm", "125 sq. cm", "100 sq. cm", "175 sq. cm"),
        ("Find the area of a trapezoid with parallel sides of 12 cm and 18 cm, and a perpendicular height of 8 cm.", "120 sq. cm", "110 sq. cm", "130 sq. cm", "144 sq. cm"),
        ("The circumference of a circular running track is 440 meters. What is its diameter? (Use π = 22/7)", "140 meters", "70 meters", "210 meters", "120 meters"),
        ("If each interior angle of a regular polygon is 140°, how many sides does the polygon have?", "9 sides", "8 sides", "10 sides", "12 sides"),
        ("What is the area of an equilateral triangle with a side length of 6 cm?", "9√3 sq. cm", "18 sq. cm", "12√3 sq. cm", "6√3 sq. cm"),
        ("The dimensions of a rectangular cuboid are 8 cm, 5 cm, and 3 cm. What is its total volume?", "120 cubic cm", "100 cubic cm", "150 cubic cm", "110 cubic cm"),
        ("How many diagonals does an octagon (8-sided polygon) have?", "20 diagonals", "16 diagonals", "24 diagonals", "18 diagonals"),
        ("An angle is equal to one-fourth of its supplementary angle. What is the measure of the angle?", "36°", "45°", "30°", "40°"),
        ("The base of a triangle is 14 cm and its altitude is 9 cm. What is the area of the triangle?", "63 sq. cm", "126 sq. cm", "54 sq. cm", "72 sq. cm"),
        ("What is the curved surface area of a cone with radius 7 cm and slant height 10 cm? (Use π = 22/7)", "220 sq. cm", "200 sq. cm", "240 sq. cm", "210 sq. cm"),
        ("If the radii of two circles are in the ratio 3:4, what is the ratio of their areas?", "9:16", "3:4", "27:64", "6:8"),
        ("A wire is bent into a circle of radius 28 cm. If it is reshaped into a square, what will be the side of the square?", "44 cm", "42 cm", "48 cm", "40 cm"),
    ]
    for q, c, w1, w2, w3 in geo_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 9. Probability & Permutations (20 questions)
    prob_scenarios = [
        ("Two fair six-sided dice are rolled. What is the probability that the sum of the numbers is 7?", "1/6", "1/12", "5/36", "1/4"),
        ("A card is drawn from a standard 52-card deck. What is the probability of drawing a King or a Queen?", "2/13", "1/13", "1/26", "4/13"),
        ("In how many distinct ways can the letters of the word 'MATH' be arranged?", "24", "12", "48", "16"),
        ("In how many ways can a committee of 3 students be selected from a group of 8 candidates?", "56", "24", "48", "64"),
        ("A fair coin is tossed 3 times. What is the probability of getting exactly two Heads?", "3/8", "1/2", "1/4", "5/8"),
        ("A box contains 5 red, 4 green, and 3 blue balls. If one ball is picked at random, what is the probability it is NOT green?", "2/3", "1/3", "3/4", "1/2"),
        ("How many 4-digit PIN numbers can be formed using the digits 0-9 if repetition of digits is allowed?", "10,000", "9,000", "5,040", "6,561"),
        ("How many distinct 4-letter words can be formed from the word 'LEADER'?", "180", "360", "720", "120"),
        ("What is the probability of drawing an Ace from a well-shuffled standard deck of cards?", "1/13", "1/52", "4/13", "1/4"),
        ("If three fair coins are flipped simultaneously, what is the probability of getting at least one Tail?", "7/8", "1/8", "3/4", "1/2"),
        ("In how many ways can 5 books be arranged on a bookshelf?", "120", "60", "24", "100"),
        ("Two cards are drawn without replacement from a deck of 52 cards. What is the probability that both are Spades?", "1/17 (13/52 * 12/51)", "1/16", "1/13", "1/26"),
        ("A bag contains 6 black balls and 4 white balls. Two balls are drawn at random. What is the probability both are black?", "1/3 (15/45)", "1/4", "2/5", "3/10"),
        ("What is the value of 7P3 (permutations of 7 items taken 3 at a time)?", "210", "35", "140", "42"),
        ("What is the value of 10C2 (combinations of 10 items taken 2 at a time)?", "45", "90", "20", "50"),
        ("A dice is thrown once. What is the probability of getting a prime number (2, 3, or 5)?", "1/2", "1/3", "2/3", "1/6"),
        ("In how many ways can 6 people sit around a circular dinner table?", "120 (5!)", "720 (6!)", "60", "360"),
        ("What is the probability of rolling a number greater than 4 on a single die roll?", "1/3", "1/2", "1/6", "2/3"),
        ("Out of 5 boys and 4 girls, a team of 4 members is to be formed. How many teams can be formed with exactly 2 boys and 2 girls?", "60", "40", "72", "50"),
        ("If event A and event B are independent, P(A) = 0.4 and P(B) = 0.5. What is P(A and B)?", "0.20", "0.90", "0.45", "0.10"),
    ]
    for q, c, w1, w2, w3 in prob_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    # 10. Number Systems, Divisibility & Sequences (20 questions)
    num_scenarios = [
        ("What is the greatest common divisor (GCD / HCF) of 48 and 72?", "24", "12", "16", "36"),
        ("What is the least common multiple (LCM) of 12, 15, and 20?", "60", "120", "90", "45"),
        ("Which of the following numbers is divisible by 9?", "45,819", "34,512", "67,811", "52,319"),
        ("What is the sum of the first 20 positive integers? (Formula: n(n+1)/2)", "210", "200", "220", "190"),
        ("Which of the following is a prime number?", "73", "87", "91", "57"),
        ("What is the remainder when 3^10 is divided by 5?", "4", "1", "2", "3"),
        ("What is the value of 1 + 2 + 3 + ... + 50?", "1,275", "1,250", "1,300", "1,225"),
        ("What is the unit digit of the product 73 * 48 * 89 * 67?", "8", "6", "4", "2"),
        ("In a geometric progression, the first term is 3 and the common ratio is 2. What is the 6th term?", "96", "48", "192", "64"),
        ("What is the smallest number which when divided by 6, 8, and 12 leaves a remainder of 2 in each case?", "26", "24", "28", "22"),
        ("How many prime numbers exist between 1 and 30?", "10", "9", "11", "8"),
        ("If the sum of three consecutive odd numbers is 57, what is the middle number?", "19", "17", "21", "15"),
        ("What is the reciprocal of the fraction 7/12?", "12/7", "7/12", "-7/12", "1/7"),
        ("What is the binary representation of the decimal number 25?", "11001", "10101", "11101", "10011"),
        ("What is the sum of the squares of the first 5 positive integers: 1^2 + 2^2 + 3^2 + 4^2 + 5^2?", "55", "50", "60", "45"),
        ("Which of the following fractions is the largest: 3/4, 5/6, 7/8, or 2/3?", "7/8", "5/6", "3/4", "2/3"),
        ("What is the difference between the place value and face value of 7 in 84,729?", "693", "700", "630", "7"),
        ("If n is an integer, (n^3 - n) is always divisible by which integer?", "6", "5", "8", "7"),
        ("Find the next term in the sequence: 2, 6, 12, 20, 30, ...", "42", "40", "44", "38"),
        ("What is the value of √0.0064?", "0.08", "0.8", "0.008", "0.0008"),
    ]
    for q, c, w1, w2, w3 in num_scenarios:
        questions.append({"text": q, "choices": [(c, True), (w1, False), (w2, False), (w3, False)]})

    return questions
