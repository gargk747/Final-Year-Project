# The package name is same as module name so!
import operator
from attr import attr, attrib

from matplotlib.pyplot import table
from nl4dv import NL4DV
import os
import json
import altair as alt
import pandas as pd
# -------------------- File INPUT ---------------------------
table_name="movies"
data_url = os.path.join(".", "examples", "assets", "data", "")
data_url = data_url+table_name+".csv"
alias_url = os.path.join(".", "examples", "assets", "aliases", "")
alias_url = alias_url+table_name+".json"
print("\nData: \n" + data_url)
print("\nAlias: \n" + alias_url)

# -------------------- Special attributes / tokens ---------------------------
# label_attribute = "Title"
# ignore_words = ['movie']
# print("\nLabel Attribute: \n" + label_attribute)
# print("\nIgnore Tokens: \n" + str(ignore_words))


# -------------------- Attribute Datatype Overrides ---------------------------
# attribute_datatypes = {"Release Year": "T"}
# print("\nAttribute Datatypes: \n" + str(attribute_datatypes))

# -------------------- QUERY INPUT ---------------------------
query = "Show average gross for different genres over the years"
# query = "Create a histogram showing distribution of IMDB ratings"
# query = "Show worldwide gross for genres Action, Adventure, Drama and Horror"
# query = "Show total gross across genres for science fiction and fantasy movies"
# query = "Relationship between budget and rating"
# query = "Show the relationship between budget and rating for Action and Adventure movies that grossed over 100M"
# query = "Show the regions having average happiness score greater than 5"
# query = "show relationship between basement area and price where home type is duplex"
# query= "Does the happiness score decrease over time"
print("\nQuery Input: \n" + query)

# -------------------- Dependency Parser (CHOOSE ONE out of the below 3 configurations) ---------------------------
dependency_parser_config = {'name': 'corenlp','model': os.path.join("examples","assets","jars","stanford-english-corenlp-2018-10-05-models.jar"),'parser': os.path.join("examples","assets","jars","stanford-parser.jar")}
# dependency_parser_config = {"name": "spacy", "model": "en_core_web_sm", "parser": None}
# dependency_parser_config = {"name": "corenlp-server", "url": "http://localhost:9000"} # requires the server to be running.

# Initialize NL4DV and set the above configurations
nl4dv_instance = NL4DV(verbose=False)
nl4dv_instance.set_data(data_url=data_url)
nl4dv_instance.set_alias_map(alias_url=alias_url)
# nl4dv_instance.set_label_attribute(label_attribute=label_attribute)
# nl4dv_instance.set_ignore_words(ignore_words=ignore_words)
# nl4dv_instance.set_attribute_datatype(attr_type_obj=attribute_datatypes)
nl4dv_instance.set_dependency_parser(config=dependency_parser_config)

# -------------------- Ask Query ---------------------------
nl4dv_response = nl4dv_instance.analyze_query(query, debug=True)


print("checking")
print(json.dumps(nl4dv_response,indent=3))
print("--------------------------------------------")



# print("select "+ " , ".join(nl4dv_response["visList"][0]["attributes"])+" from TABLE_NAME where "+nl4dv_response["taskMap"]["filter"][0]["attributes"][0]+" is "+nl4dv_response["taskMap"]["filter"][0]["queryPhrase"]+ " than "+ str(nl4dv_response["taskMap"]["filter"][0]["values"][0])) 
where = []
baseSQL="Select * from "+table_name
attributes=[]
for i in nl4dv_response["visList"]:
    if("x" not in i["vlSpec"]["encoding"] or "y" not in i["vlSpec"]["encoding"]):
        continue
    if([i["vlSpec"]["encoding"]["x"]["field"],i["vlSpec"]["encoding"]["y"]["field"]] not in attributes):
        attributes.append([i["vlSpec"]["encoding"]["x"]["field"],i["vlSpec"]["encoding"]["y"]["field"]])
    if("color" in i["vlSpec"]["encoding"]):
        if([i["vlSpec"]["encoding"]["x"]["field"],i["vlSpec"]["encoding"]["y"]["field"],i["vlSpec"]["encoding"]["color"]["field"]] not in attributes):
            attributes.append([i["vlSpec"]["encoding"]["x"]["field"],i["vlSpec"]["encoding"]["y"]["field"],i["vlSpec"]["encoding"]["color"]["field"]])
    if("column" in i["vlSpec"]["encoding"]):
        if([i["vlSpec"]["encoding"]["x"]["field"],i["vlSpec"]["encoding"]["y"]["field"],i["vlSpec"]["encoding"]["column"]["field"]] not in attributes):
            attributes.append([i["vlSpec"]["encoding"]["x"]["field"],i["vlSpec"]["encoding"]["y"]["field"],i["vlSpec"]["encoding"]["column"]["field"]])
finalAttributes = []
for i in attributes:
    if(len(i)>2):
        if(i[2]!=i[0] and i[2]!=i[1]):
            finalAttributes.append(i)
    else:
        finalAttributes.append(i)

diff = 0

for i in finalAttributes:
    if(len(i)==2):
        if(i[0]!=i[1]):
            diff = 1
            break
if(diff==0):
    for i in nl4dv_response['attributeMap']:
        for j in nl4dv_response['attributeMap']:
            if(i!=j):
                finalAttributes.append([i,j])


taskMap = nl4dv_response['taskMap']
finalSQLquery=baseSQL
if("trend" in taskMap or 'coorelation' in taskMap):
    finalSQLquery=baseSQL
    # finalAttributes=baseAttribute
if('filter' in taskMap):
    for i in (taskMap["filter"]):
        if(i["operator"]=="GT"):
            where.append("".join("`" + i["attributes"][0] + "`" + ">" + str(i["values"][0])))
        elif(i["operator"]=="LT"):
            where.append("".join("`" + i["attributes"][0] + "`" + "<" + str(i["values"][0])))
        elif(i["operator"]=="IN"):
            where.append("".join("`" + i["attributes"][0] + "`" + " IN (\"" + "\", \"".join(i["values"])+"\")"))
        elif(i["operator"]=="AVG"):
            where.append("".join("AVG("+"`" + i["attributes"][0] + "`" + ") is " + str(i["values"]))) 
    finalSQLquery = baseSQL + " where " + " and ".join(where)     
# if("derived_value" in taskMap):
#     for i in (taskMap["derived_value"]):
#         if(i["operator"]=="SUM"):
#             attributes.append(" SUM("+i["attributes"][0]+")")
#         if(i["operator"]=="AVG"):
#             attributes.append(" AVG("+i["attributes"][0]+")")
#         if(i["operator"]=="COUNT"):
#             attributes.append(" COUNT("+i["attributes"][0]+")")
#     finalAttributes=baseAttribute+" ,"+" , ".join(attributes)


print(finalSQLquery)
print(finalAttributes)

finalSQLquery=finalSQLquery+'\n'
file1=open(r'C:\Users\gargk\Desktop\MNIT\Final Year Project\DeepEye\APIs_Deepeye\input.txt','w')
file1.write(finalSQLquery)
file1.write(str(finalAttributes))
file1.close()

# data = pd.read_csv(r"https://raw.githubusercontent.com/gargk747/FYP-DataSet/master/movies-w-year.csv")
# for vl in nl4dv_response["visList"]:
#     alt.Chart.from_dict(vl["vlSpec"]).show()





# -------------------- NL4DV Response ---------------------------
# print("\nData Attribute Map:")
# print(nl4dv_instance.data_genie_instance.data_attribute_map)
# print("-----------------------------------------")

# print("\nAttributes List:")
# print(nl4dv_response['attributeMap'].keys())

# print("\nAttributeMap:")
# print(json.dumps(nl4dv_response['attributeMap'],indent=3))
# print("-----------------------------------------")

# print("\nTasks:")
# print("\nList of Tasks:")
# print(nl4dv_response['taskMap'].keys())

# print("\nTaskMap:")
# print(nl4dv_response['taskMap'])
# print("-----------------------------------------")




# print("\nList of Vis marks:")
# print([vis_obj["vlSpec"]["mark"]["type"] for vis_obj in nl4dv_response['visList']])

# print("\nVisList:")
# print(nl4dv_response['visList'])
# print("-----------------------------------------")

# print("\nFull Output:")
# print(json.dumps(nl4dv_response["visList"], indent=4))
# print("-----------------------------------------")