#World Data Structures
import csv 
import datetime
print("Running")
countries = []
with open('CountryData/CSVfiles/Population.csv') as fh:
    reader = csv.DictReader(fh)
    for entry in reader:
        pop = int((entry['Population']).replace(',',''))
        if pop > 1900000:
            countries.append(entry['Country'])
    fh.close()


#Population
pop_dict = {}
pop_list = []
small_pop = []
with open('CountryData/CSVfiles/Population.csv') as fh:
    reader = csv.DictReader(fh)
    for entry in reader:
        pop_dict[entry['Country']]= int((entry['Population']).replace(',',''))

for country in countries:
    pop_list.append(pop_dict.get(country, None))
for country in pop_list:
    x = 1000000
    small_pop.append(country/x) #If using small pop Global population is aproximately (7,000,000,000 / x)

#GDP
gdp_dict = {}
gdp_list = []
with open('CountryData/CSVfiles/UN_GDP.csv') as fh:
    reader = csv.DictReader(fh)
    for entry in reader:
        gdp_dict[entry['Country']]= float(entry['Value'])

for country in countries:
    gdp_list.append(gdp_dict.get(country, None))    

#Unemployment
unem_dict = {}
unem_list = []
with open('CountryData/CSVfiles/CIA_Unemployment.csv') as fh:
    reader = csv.DictReader(fh)
    for entry in reader:
        unem_dict[entry['Country']]= float(entry['Unemployment'])

for country in countries:
    unem_list.append(unem_dict.get(country, None))

#Neighbors
ne_dict = {}
ne_list = []
abrvs = {}
with open('CountryData/CSVfiles/Neighbors.csv') as fh:
    reader = csv.DictReader(fh)
    for entry in reader:
        abrvs[entry['iso_alpha2']] = entry['Country']
with open('CountryData/CSVfiles/Neighbors.csv') as file:
    reader = csv.DictReader(file)
    for entry in reader:
        ne_abrvs = entry['neighbors'].split()
        neighbors = []
        for abrv in ne_abrvs:
            neighbors.append(abrvs[abrv])
        ne_dict[entry['Country']]= neighbors
    ne_dict['Madagascar'] = ['Mozambique']

for country in countries:
    ne_list.append(ne_dict.get(country, None))
#Population of Attachment to household file

attachment_dict = {}
attachment_list = []
with open('CountryData/CSVfiles/attachment.csv') as fh:
    reader = csv.DictReader(fh)
    
    for entry in reader:
            score =  (float(entry['Total fertility rate']))
    country = entry['Country'].split(',')[0]
    attachment_dict[country] = score 
for country in countries:
    attachment_list.append(attachment_dict.get(country, None))  

#Armed Conflict File
conflict_dict = {}
conflict_list = []
with open('CountryData/CSVfiles/Mainconflicttable.csv') as fh:
    reader = csv.DictReader(fh)
    for entry in reader:
        score = ((int(entry['YEAR']) - 1946) / 10) * (int(entry['Intensity'])**2)
        country = entry['Country'].split(',')[0]
        if country == 'Russia (Soviet Union)':
            country = 'Russia'
        elif country == 'Hyderabad':
            country = 'India'
        elif 'Yemen' in country:
            country = 'Yemen'
        elif country == 'United States of America':
            country = 'United States'
        elif 'Vietnam' in country:
            country = 'Vietnam'
        elif country == 'Democratic Republic of Congo (Zaire)':
            country = 'Democratic Republic of the Congo'
        elif country == 'Guinea-Bissau':
            country = 'Guinea'
        elif country == 'Sri Lanka (Ceylon)':
            country = 'Sri Lanka'
        elif country == 'Zimbabwe (Rhodesia)':
            country = 'Zimbabwe'
        elif country == 'Turkey/Ottoman Empire':
            country = 'Turkey'
        elif country == 'Yugoslavia (Serbia)':
            country = 'Serbia'
        elif country == 'Cote DÕIvoire':
            country = "Cote d'Ivoire"
        elif country == 'Rumania':
            country = 'Romania'

        conflict_dict[country]= conflict_dict.get(country, 0) + score

for country in countries:
    conflict_list.append(conflict_dict.get(country, 0))

#Fill in missing entries
def fillData(l, d):
    '''Fill in missing data using values from neighboring countries. If there is 
    not data for all neighboring countries, theglobal average value is used.'''
    for i, country in enumerate(countries):
        if l[i] == None:
            switch = True
            n = 0
            while switch and n < len(ne_list[i]):
                if d.get(ne_list[i][n], False):
                    l[i] = d[ne_list[i][n]]
                    switch = False
                n += 1
        if l[i] == None:
            tot = 0
            count = 0
            for value in l:
                if value != None:
                    tot += value
                    count += 1
            avg = float(tot) / count
            l[i] = avg

fillData(unem_list, unem_dict)
fillData(gdp_list, gdp_dict)
fillData(conflict_list, conflict_dict)
fillData(attachment_list, attachment_dict)

#Create country ID strings
c_ids = []

for c in range(len(countries)):
    if c < 10:
        c_id = '00' + str(c)
    elif c < 100:
        c_id = '0' + str(c)
    else:
        c_id = str(c)
    c_ids.append(c_id)

import random

def populate_world(small = True):
    world = []
    if small == True:
        population = small_pop
    else:
        population = pop_list
    for c in range(len(countries)): #c = index of a country
        world.append([])
        for n in range(10): #n = index of a neighborhood
            world[c].append([])
            for i in range(int(population[c]/10)):
                
                #Generate E1 (income) value for each person
                E1_rand_n = random.triangular(0,2.5,.5) #Creates a right skewed distribution with mean aproximately 1
                E1 = gdp_list[c] * E1_rand_n
                
                  #Generate E2 (employment status; 0 = unemployed) 
                E2_rand_n = random.random()
                if E2_rand_n * 100 >= unem_list[c]:
                    E2 = 1
                else:
                    E2 = 0
                
                #Generate S2 (Attachment to Family)
                    #Used a triangular distribution with min at 0 and max at 2
                S2_rand_n= random.triangular(0,2,1)
                S2 = S2_rand_n * attachment_list[c]
                #Add person to country
                person = (S2, E1, E2, c_ids[c])
                world[c][n].append(person)
    return world

def gen_history():
    '''Generate Blank Migration History Table'''

    mig_history = []
    for c in range(len(countries)):
        c_hist = []
        for c in range(len(countries)):
            value = 0    #version 2: use historical data here
            c_hist.append(value)
        mig_history.append(c_hist)
    return mig_history

print("Populating the world")
world = populate_world()
print("Populated")
print("Generating history")
mig_history = gen_history()
print("Generated")

MAX_M = 10 + 10 + 10 + 7

def ifMig(person, country, max_values, M_THRESHOLD, BD_THRESHOLD):
    '''Returns True if person decides to migrate based on individual values'''
    
    max_conflict = max_values[0]
    
    S1 = float(conflict_list[country])/ max_conflict * 10
    S2 = float(person[0]) / (attachment_list[country] * 2) * 10
   
    if person[1] < (BRAIN_DRAIN_THRESHOLD * (gdp_list[country] * 2.5)):
        E1 = 10 - (((float(person[1])) / (gdp_list[country] * 2.5)) * ((gdp_list[country]/max_values[2])) * 10)
    else:
        E1 = 10 * ( 1 - (gdp_list[country]/max_values[2]))
              
    E2 = (float(person[2]) * 4) + 3
    
    M = (S1 + S2 + E1 + E2) / MAX_M #Individual willingness to migrate value
    if M > M_THRESHOLD:
        return True
    return False

def calculate_AM(origin_country):
    '''Creates a list of AM values for each country. NOTE: AME3 is calculated as needed in where_Mig function
    If max_values = True also returns a list of maximum raw values for each AM statistic'''
    AM_values = []
    max_conflict = 0
    max_family = 0
    max_income = 0
    max_unem = 0
    max_hist = 1
    
    for n in conflict_list:
        if n > max_conflict:
            max_conflict = n
    for n in attachment_list: 
        if n > max_family:
            max_family = n
    for n in gdp_list:
        if n > max_income:
            max_income = n
    for n in unem_list:
        if n > max_unem:
            max_unem = n
    for n in mig_history[origin_country]:
        if n > max_hist:
            max_hist = n

    for i in range(len(countries)):
        #AMS1 (Conflict level in country)
        AMS1 = float(conflict_list[i])/ max_conflict * 10 
        #AMS2 (Migration history)
        AMS2 = float(mig_history[origin_country][i]) / max_hist * 10
        #AME1 (Per capita GDP)
        AME1 = (float(gdp_list[i]) / max_income) * 10
        #AME2 (Unemployemnt rate)
        AME2 = (float(unem_list[i]) / max_unem) * 10
        #AME3 (Neighbor Attractiveness)
        c_str = countries[origin_country]
        if c_str in ne_list[i]:
            AME3 = 10
        else:
            AME3 = 2
        
        AM_values.append((AMS1, AMS2, AME1, AME2, AME3))
        
    return AM_values, [max_conflict, max_family, max_income, max_unem, max_hist]
    
def where_Mig(country):
    '''Returns the index of the destination country for a migrating individual'''
    AMs = []
    c_str = countries[country]
    for i in range(len(countries)):
        if c_str in ne_list[i]:
            AME3 = 100
        else:
            AME3 = 20
        AMS1 = AM_values[i][0] * 100
        AMS2 = AM_values[i][1] * 100
        AME1 = AM_values[i][2] * 100
        AME2 = AM_values[i][3] * 100
        AME3 = AM_values[i][4] * 100
        AM = AMS1 + AMS2 + AME1 + AME2 + AME3
        for n in range(int(AM)):
            AMs.append(i)
    
    return random.choice(AMs)
    
def migrate(person, origin, destination):
    '''Adds person p to country (where country is the index of the destination country)'''
    
    neighborhood = random.randint(0,9) #Chooses a random neighborhood to move to
    
    c_hist = person[3]
    c_hist += c_ids[destination]
    mig_history[origin][destination] += 1
    
    new_person = (person[0], person[1], person[2], c_hist)
                                                    
    world[destination][neighborhood].append(new_person)

# Testing one step of global migration
M_THRESHOLD = 0.75 # 1 = no migration; 0 = everyone migrates
BRAIN_DRAIN_THRESHOLD = 0.05
net_migrations = {}

x = datetime.datetime.now()

print("Running migration")
for c, country in enumerate(world):
    AM_values, max_values = calculate_AM(c)
    for n, neighborhood in enumerate(country):
        for p, person in enumerate(neighborhood):
                if ifMig(person, c, max_values, M_THRESHOLD, BRAIN_DRAIN_THRESHOLD):
                    destination = where_Mig(c)
                    migrate(person, c, destination)
                    del world[c][n][p]
                    #Track this in unique list for each country
                    net_migrations[countries[c]] = net_migrations.get(countries[c], 0) - 1
                    net_migrations[countries[destination]] = net_migrations.get(countries[destination], 0) + 1
y = datetime.datetime.now()
print("Done")
print(net_migrations)

with open('base_log', 'w')as fh:
    fh.write('Start: ' + str(x) + '\n')
    fh.write('End: ' + str(y) + '\n')
    fh.write('Total: '+ str(y-x)+ '\n')

def count_population(world):
    '''Counts the current population of the world'''
    pop = 0
    for country in world:
            for neighborhood in country:
                pop += len(neighborhood)
    return pop
print(count_population(world))
