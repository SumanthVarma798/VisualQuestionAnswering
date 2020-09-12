# Requires python 2.7

from SPARQLWrapper import SPARQLWrapper, JSON

def SelectQueryEngine(item, query, Type):
  
  item = item.lower()
  item = item.title()
  final_answer_list = []
  sparql = SPARQLWrapper("http://dbpedia.org/sparql")
  sparql.setQuery("""
    PREFIX db: <http://dbpedia.org/resource/>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbp: <http://dbpedia.org/property/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX wiki: <https://en.wikipedia.org/wiki/>
    SELECT ?value
    WHERE {
      db:%s %s:%s ?value
    }
  """%(item,Type,query))
  sparql.setReturnFormat(JSON)
  results = sparql.query().convert()

  for result in results["results"]["bindings"]:
    if query == 'abstract':
      if result[u'value'][u'xml:lang'] == u'en':
        final_string = result[u'value'][u'value']
        final_answer_list.append(final_string)
    else:
      final_string = result[u'value'][u'value']
      tokens = final_string.split('/')
      final_answer_list.append(str(tokens[-1]))
  
  return final_answer_list

def SelectPropertyQueryEngine(item):

  rdf_props = []
  rdfs_props = []
  dbp_props = []
  dbo_props = []
  props_dict = {}   
  sparql = SPARQLWrapper("http://dbpedia.org/sparql")
  sparql.setQuery("""
    PREFIX db: <http://dbpedia.org/resource/>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbp: <http://dbpedia.org/property/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX wiki: <https://en.wikipedia.org/wiki/>
    SELECT ?property ?value
    WHERE {
      db:%s ?property ?value
    }
  """%(item))
  sparql.setReturnFormat(JSON)
  results = sparql.query().convert()

  for result in results["results"]["bindings"]:
    result_string = str(result[u'property'][u'value'])
    result_string_tokens = result_string.split("/")
    rdf_and_rdfs_split = result_string_tokens[-1].split("#")
    if '22-rdf-syntax-ns' in rdf_and_rdfs_split:
      if rdf_and_rdfs_split[-1] not in rdf_props:
        rdf_props.append(rdf_and_rdfs_split[-1])
    elif 'rdf-schema' in rdf_and_rdfs_split:
      if rdf_and_rdfs_split[-1] not in rdfs_props:
        rdfs_props.append(rdf_and_rdfs_split[-1])
    elif 'property' in result_string_tokens:
      if result_string_tokens[-1] not in dbp_props:
        dbp_props.append(result_string_tokens[-1])
    elif 'ontology' in result_string_tokens:
      if result_string_tokens[-1] not in dbo_props:
        dbo_props.append(result_string_tokens[-1])

  props_dict['rdf'] = rdf_props
  props_dict['rdfs'] = rdfs_props
  props_dict['dbp'] = dbp_props
  props_dict['dbo'] = dbo_props

  return(props_dict)

def AskQueryEngine(item, query, Type, isthis):
    
  item = item.title()
  sparql = SPARQLWrapper("http://dbpedia.org/sparql")
  sparql.setQuery("""
    PREFIX db: <http://dbpedia.org/resource/>
    PREFIX dbo: <http://dbpedia.org/ontology/>
    PREFIX dbp: <http://dbpedia.org/property/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    PREFIX wiki: <https://en.wikipedia.org/wiki/>
    ASK WHERE {
      db:%s %s:%s "%s"@en
    }
  """%(item,Type,query,isthis))
  sparql.setReturnFormat(JSON)
  results = sparql.query().convert()
  
  return bool(results[u'boolean'])

def AnimalSame(animal1, animal2):
  retlis1 = SelectQueryEngine(str(animal1), 'taxon', 'dbp')
  retlis2 = SelectQueryEngine(str(animal2), 'taxon', 'dbp')
  flag = 0
  for val1 in retlis1:
    for val2 in retlis2:
      if val1 == val2:
        print("{} and {} belong to the same {} taxonomy".format(animal1, animal2, val1))
        flag = 1
        break
  if not flag:
    print("{} and {} do not belong to the same taxonomy".format(animal1, animal2))

def AnimalClass(animal):
  flag = 1
  retlis = SelectQueryEngine(str(animal), 'taxon', 'dbp')
  if not retlis:
    retlis = SelectQueryEngine(str(animal), 'genus', 'dbp')
    if not retlis:
      retlis = SelectQueryEngine(str(animal), 'phylum', 'dbo')
      if not retlis:
        print("No animal class found for {} try another animal.".format(str(animal)))
        flag = 0
  if flag:
    print("The following is/are the Animal Class of {}:".format(str(animal)))
    for item in retlis:
      print("\t%s"%item)

def FoodIngredient(food):
  retlis = SelectQueryEngine(str(food), 'ingredient', 'dbo')
  if not retlis:
    print("Failed to find ingredients in {}, try a different one...".format(str(food)))
  else:
    print("The following is/are the ingredients of {}:".format(str(food)))
    for item in retlis:
      print("\t%s"%item)

def SportEquip(sport):
  retlis = SelectQueryEngine(str(sport), 'equipment', 'dbo')
  if not retlis:
    print("Failed to find equipments for {}, try a different one...".format(str(sport)))
  else:
    print("The following is/are the equipments for {}:".format(str(sport)))
    for item in retlis:
      print("\t%s"%item)

def PlaceCapitals(place):
  retlis = SelectQueryEngine(str(place), 'capital', 'dbo')
  if not retlis:
    print("Failed to find capital for {}, try a different one...".format(str(place)))
  else:
    if len(retlis) > 1:
      print("The following are the capitals of {}:".format(str(place)))
      for item in retlis:
        print("\t%s"%item)
    else:
      print("{} is the capital of {}:".format(str(retlis[0]), str(place)))

def TellMeAbout(query):
  retlis = SelectQueryEngine(str(query), 'abstract', 'dbo')
  if not retlis:
    print("Failed to find more information on {}, try a different one...".format(str(query)))
  else:
    print("The following is a little stuff about {}:".format(str(query)))
    for item in retlis:
      print("\t%s"%item)

def WhatIs(obj):
  retlis = SelectQueryEngine(str(obj), 'label', 'rdfs')
  if not retlis:
    print("Failed to find what {} is, try a different one...".format(str(obj)))
  else:
    print("{} is {}:".format(str(obj), str(retlis[0])))


def AnimalRelative(animal):#Not Working, Need to find a good predicate to search for
  retlis = SelectQueryEngine(str(animal), 'sameAs', 'owl')
  if not retlis:
    print("Failed to find close relatives of {}, try a different one...".format(str(animal)))
  else:
    print("The following are some of the close relatives of {}:".format(str(animal)))
    for item in retlis:
      print("\t%s"%item)

def IsTheA(obj, concept):# Working with limited functionality
  properties_list = []
  property_dict = SelectPropertyQueryEngine(str(obj))
  if len(property_dict) == 0:
    print("Failed to retrieve properties for {}.".format(str(obj)))
  else:
    level_1_lists = property_dict.values()
    for level_2_lists in level_1_lists:
      for prop in level_2_lists:
        properties_list.append(str(prop))
  flag = 1
  for queried_prop in properties_list:
    if queried_prop in property_dict['rdf']:
      if AskQueryEngine(str(obj), str(queried_prop), 'rdf', str(concept)):
        print("Yes, {}'s {} is {}.".format(str(obj),str(queried_prop).lower() , str(concept)))
        flag = 0
        break
    elif queried_prop in property_dict['rdfs']:
      if AskQueryEngine(str(obj),str(queried_prop), 'rdfs', str(concept)):
        print("Yes, {}'s {} is {}.".format(str(obj),str(queried_prop).lower() , str(concept)))
        flag = 0
        break
    elif queried_prop in property_dict['dbp']:
      if AskQueryEngine(str(obj),str(queried_prop), 'dbp', str(concept)):
        print("Yes, {}'s {} is {}.".format(str(obj),str(queried_prop).lower() , str(concept)))
        flag = 0
        break
    elif queried_prop in property_dict['dbo']:
      if AskQueryEngine(str(obj),str(queried_prop), 'dbo', str(concept)):
        print("Yes, {}'s {} is {}.".format(str(obj),str(queried_prop).lower() , str(concept)))
        flag = 0
        break
    else: flag = 1
  if flag:
    print("No, {} is not {}.".format(str(obj), str(concept)))

def CommonProp(obj1, obj2): #Not Working
  retlis1 = SelectQueryEngine(str(obj1), 'type', 'rdf')
  retlis2 = SelectQueryEngine(str(obj2), 'type', 'rdf')
  similar_stuff = []
  for val1 in retlis1:
    for val2 in retlis2:
      if val1 == val2:
        similar_stuff.append(val1)
  if not similar_stuff:
    print("{} and {} have no common properties".format(obj1, obj2))
  else:
    print("The following are the common properties of {} and {}:".format(obj1, obj2))
    for item in similar_stuff:
      print("\t%s"%item)

def ItemInfo(obj):
  property_dict = SelectPropertyQueryEngine(str(obj))
  if len(property_dict) == 0:
    print("Failed to retrieve properties for {}.".format(str(obj)))
  else:
    print("The following are the properties of {}:".format(str(obj)))
    level_1_lists = property_dict.values()
    for level_2_lists in level_1_lists:
      for prop in level_2_lists:
        print("\t%s"%(prop))

  queried_prop = raw_input("\nWhat property do you want to query?\nType Here:\t")
  print("\n")
  if queried_prop in property_dict['rdf']:
    retlis = SelectQueryEngine(str(obj), str(queried_prop), 'rdf')
    if not retlis:
      print("Failed to find {} for {}, try a different one...".format(str(queried_prop), str(obj)))
    else:
      print("The following is/are the {} for {}:".format(str(queried_prop), str(obj)))
      for item in retlis:
        print("\t%s"%item)
  elif queried_prop in property_dict['rdfs']:
    retlis = SelectQueryEngine(str(obj), str(queried_prop), 'rdfs')
    if not retlis:
      print("Failed to find {} for {}, try a different one...".format(str(queried_prop), str(obj)))
    else:
      print("The following is/are the {} for {}:".format(str(queried_prop), str(obj)))
      for item in retlis:
        print("\t%s"%item)
  elif queried_prop in property_dict['dbp']:
    retlis = SelectQueryEngine(str(obj), str(queried_prop), 'dbp')
    if not retlis:
      print("Failed to find {} for {}, try a different one...".format(str(queried_prop), str(obj)))
    else:
      print("The following is/are the {} for {}:".format(str(queried_prop), str(obj)))
      for item in retlis:
        print("\t%s"%item)
  elif queried_prop in property_dict['dbo']:
    retlis = SelectQueryEngine(str(obj), str(queried_prop), 'dbo')
    if not retlis:
      print("Failed to find {} for {}, try a different one...".format(str(queried_prop), str(obj)))
    else:
      print("The following is/are the {} for {}:".format(str(queried_prop), str(obj)))
      for item in retlis:
        print("\t%s"%item)
  else: print("Invalid Property selected!, Select another property.")