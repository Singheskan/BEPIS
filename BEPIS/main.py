from py2neo import Graph  # https://py2neo.org/v4/
from random import randint, uniform
# For evaluation purposes
import names
import time
import csv
import os

'''
Fraunhofer Institut für Sichere Informationstechnologie
Author: Patrick Singh
Betreuer: Hervais-Clemence Simo Fhom, Prof. Michael Waidner
'''
'''
BEPIS - Description:
BEPIS is an experimental approach on realizing Epsilon-Differential-Privacy as data anonymization technique for
graph database, e.g. Neo4j. It provides a console interface to a running Neo4j-Graph instance and ways to laod data
into the system, as .csv files. Furthermore, it provides ways to query the database and translates these queries to queries
enforcing epsilon-differential-privacy. As being a prove-of-concept implementation as part of my bachelor thesis,
it only provides first-steps into this topic and is therefore just providing a translation for aggregation queries, like counting queries.
We are implementing the sensitivity-based mechanism with elastic sensitivity as an upper boundary to local sensitivity.
Concretely, we are applying a smoothing function on top of local sensitivity to ensure a certain distance to the true database.
'''
'''
Sending queries to the Neo4j Browser to visualize them is currently not possible:
https://community.neo4j.com/t/py2neo-can-we-see-in-a-client-navigator-the-query-send-by-py2neo/1674/3
https://github.com/neo4j/neo4j-browser/issues/728

-> Queries must be inserted into the Neo4j Browser by hand to visualize them properly.

Loadable CSV-Files: UserData.csv (100 entries), UserData2.csv (10.000 entries), UserData3.csv (500.000 entries)
'''


class EDPNeo4j:
    # Neo4j Graph Credentials
    uri = "bolt://localhost:7687"  # Neo4j Browser - :server status
    user = "neo4j"
    password = "snsnsn11"
    running = True

    # Privacy Budget, Epsilon, sensitivity, and database-distance k
    pb = 10
    initPB = pb  # for testing
    eps = 0.1
    s = 1  # Depending on the queries inherent sensitivity
    k = 1  # standardized to local sensitivity

    # Query (I), (II), and (III) mentioned in thesis
    q1 = "MATCH(n) RETURN count(n)"
    q2 = "MATCH(n)-[r]-() RETURN count(r)"
    q3 = "MATCH (n: Person)-[r: NameASenior]-(p: Person) WHERE n.income>2000 AND p.income<3000 AND n.age>62" \
         " AND p.age<66 AND NOT (n)-[r]-(n) AND (NOT p.name STARTS WITH 'n' OR NOT n.name STARTS WITH 'p') " \
         "RETURN count(r)"

    try:
        g = Graph(uri=uri, user=user, password=password)
    except ConnectionError:
        print("Check if a (local) instance of Neo4j is up and running, "
              "as well as if the graph address (uri), user and password match")

    # clear the graph, adapt LIMIT value if not enough memory
    while len(g.nodes) > 0:
        print("Deleting Nodes: " + str(len(g.nodes)) + " and relations: " + str(len(g.relationships)))
        g.run("MATCH(n) WITH n LIMIT 10000 DETACH DELETE n")

    # Add / uncomment the following line in neo4j.conf: dbms.directories.import=import
    # Insert csv files: (create import folder if missing)
    # in windows: C:\Users\username\.Neo4jDesktop\neo4jDatabases\database-xxxx-xxxx\installation-x.x.x\import
    print("Please insert a csv file into Neo4j's import folder before continuing.")
    csvName = input(
        "Please insert the name of the csv file (format name.csv) or type nothing to use UserData3.csv: ")
    if not csvName:  # Empty strings are considered false boolean
        csvName = "UserData3.csv"
        csvURL = "\"file:///UserData3.csv\""  # csv is in import folder of the neo4j distribution
    else:
        csvURL = "\"file:///" + csvName + "\""

    # Insert a custom value for loading a part of the csv file
    lineLimit = input("Please insert a line limit if you do not wish to load the complete csv file: ")
    if not lineLimit and csvName == "UserData.csv":
        lineLimit = 100
    elif not lineLimit and csvName == "UserData2.csv":
        lineLimit = 10000
    elif not lineLimit and csvName == "UserData3.csv":
        lineLimit = 40000  # out of performance reasons, normal upper boundary 500000
    oldLineLimit = lineLimit  # for tests

    # CSV Files (size: 100 and 10.000) generated with: http://www.convertcsv.com/generate-test-data.htm
    # One must specify new loading schemes for other .csv files
    if csvName == "UserData.csv" or csvName == "UserData2.csv" or csvName == "UserData3.csv":
        csvLoad = g.run("LOAD CSV WITH HEADERS FROM " + csvURL +
                        " AS line WITH line LIMIT " + str(lineLimit) + " CREATE (:Person "
                                                                       "{ name: line.name, gender: line.gender, age: toInteger(line.age), "
                                                                       "city: line.city, income: toFloat(line.income) })")
    else:
        print("There is no loading scheme specified for this csv file.")

    # Begin a transaction
    tx = g.begin()
    # Interconnect some nodes as "Friends" or "Foes"
    # Point of most computation time, therefore not applicable to UserData3.csv
    if csvName == "UserData.csv" or csvName == "UserData2.csv":
        tx.run(
            "MATCH (a: Person), (b: Person) WHERE a.name STARTS WITH 'A' AND b.name STARTS WITH 'B' "
            "CREATE (a)-[r:Friends]->(b)")
        tx.run(
            "MATCH (a: Person), (b: Person) WHERE a.name STARTS WITH 'C' AND b.name STARTS WITH 'D' "
            "CREATE (a)-[r:Foes]->(b)")

    # if csvName == "UserData3.csv":  # add relations for testing
    #    g.run("Match(a: Person), (b: Person) WHERE a.age>63"
    #          " and a.name STARTS WITH 'A' and b.age>63 CREATE (a)-[r: NameASenior]->(b)")

    # Transfer changes to neo4j graph application
    # Once a transaction has been committed or rolled back, it is marked as 'finished' and cannot be reused
    tx.commit()
    print("After commit")
    print("Nodes: " + str(len(g.nodes)))
    print("Relations: " + str(len(g.relationships)))

    # Optional: Further Instructions before querying
    furtherInstr = input("You can enter further instructions before querying, if not necessary, press enter: ")
    if furtherInstr:
        ty = g.begin()
        ty.run(furtherInstr)
        ty.commit()
        print("After further instructions")
        print("Nodes: " + str(len(g.nodes)))
        print("Relations: " + str(len(g.relationships)))

    # Setting DB Metadata for sensitivity calculation
    originDBNodeCount = len(g.nodes)

    # Set k-distance
    kDistanceInput = input("Set a custom distance k for the database, press enter for k=1: ")
    if kDistanceInput and k > originDBNodeCount:
        print("k was set to high")
        k = 1
    elif kDistanceInput:
        k = int(kDistanceInput)

    userQuery = input(
        "Please insert a Cypher Query, 1, 2, or 3, for inserting the three queries specified in the thesis, "
        "or type nothing to enter 'MATCH(n) RETURN count(n): ")
    if not userQuery:
        userQuery = "MATCH(n) RETURN count(n)"
    if userQuery == "1":
        userQuery = q1
    elif userQuery == "2":
        userQuery = q2
    elif userQuery == "3":
        userQuery = q3

    oldK = k  # for tests
    # Compute k-distant graph, not fully dependent on the query
    timeKStart = time.time()  # start time measuring
    while int(k) > 0:
        tu = g.begin()

        if "Female" in userQuery:
            tu.run("CREATE (n: Person { name: '" + names.get_full_name(gender="female") + "', age: " + str(
                randint(20, 80)) + ", city: 'Springfield', income: " + str(
                round(uniform(1000.0, 9000.0), 2)) + "})")
            tu.commit()
        elif "Male" in userQuery:
            tu.run("CREATE (n: Person { name: '" + names.get_full_name(gender="male") + "', age: " + str(
                randint(20, 80)) + ", city: 'Springfield', income: " + str(
                round(uniform(1000.0, 9000.0), 2)) + "})")
            tu.commit()
        else:
            tu.run("CREATE (n: Person { name: '" + names.get_full_name() + "', age: " + str(
                randint(20, 80)) + ", city: 'Springfield', income: " + str(
                round(uniform(1000.0, 9000.0), 2)) + "})")
            tu.commit()

        k = k - 1

    timeKEnd = time.time()
    timeK = timeKEnd - timeKStart
    print("Computation time of k: " + str(timeK))

    # Sensitivity Computation
    choiceSensitivity = input(
        "Do you want to compute a custom sensitivity (1), set your own (2), or use the default value (3)?: ")

    if choiceSensitivity == "1":
        timeSStart = time.time()
        s = 1 + originDBNodeCount / next(iter(g.run(userQuery).data().pop().values()))
        timeSEnd = time.time()
        timeS = timeSEnd - timeSStart
        print("Sensitivity: " + str(s))
        print("Computation time of s: " + str(timeS))
    elif choiceSensitivity == "2":
        s = input("Insert a sensitivity between 1 and 10: ")
        timeS = 0
    else:
        timeS = 0

    if int(s) > 10:
        s = 10

    if userQuery:
        EDPQueryStart = time.time()  # start time measurement for anonymizing the query
        # Reduce PB
        # querying for unique identifiers is most sensitive and should never result in feasible output, for now
        if not "count" in userQuery:
            print("Very sensitive")
            pb = 0

        print("Translating Cypher Query to be Epsilon-Differentially-Private")
        # Check if query is a counting query - aggregation function and pb not exhausted
        if "count" in userQuery and pb > 0:
            print("Apply Sensitivity-Based Mechnism on Counting Query")
            orig = g.begin()
            saveOrig = next(iter(orig.run(userQuery).data().pop().values()))  # Only label for test query
            uniform = g.begin()
            saveUniform = next(
                iter(uniform.run("Match(n) return rand()-0.5 limit 1").data().pop().values()))
            countQuery = g.begin()
            # Applying Laplacian-Noise as locally sensitive method
            countQuerySave = round(next(iter(countQuery.run(
                "Match(n) return " + str(saveOrig) + "-(" + str(s) + "/" + str(eps) + ")*sign("
                + str(saveUniform) + ")*log(1-2*abs(" + str(saveUniform) + ")) limit 1").data().pop().values())))
            print(
                "Match(n) return " + str(saveOrig) + "-(" + str(s) + "/" + str(eps) + ")*sign("
                + str(saveUniform) + ")*log(1-2*abs(" + str(saveUniform) + ")) limit 1")
            print("\n" + "---------- EDP Query Result: " + str(countQuerySave) + "----------\n")
            countQuery.commit()
            pb = pb - int(s)  # Reduce Privacy Budget

            EDPQueryEnd = time.time()
            EDPQueryTime = EDPQueryEnd - EDPQueryStart
            # print("Computation Time of EDP Query: " + str(EDPQueryTime))
            TotalCompTime = timeK + timeS + EDPQueryTime
            # print("Total Computation Time of EDP: " + str(TotalCompTime))

        else:
            print("Currently, there are no ways implemented to anonymize this kind of query.")

        '''
        This chapter is executing performance tests for BEPIS and delivers a basis for the evaluation chapter in the thesis.
        A deployment of BEPIS in practice should not enable access to this part, as it enables direct access to the concrete database.
        '''

        # Measuring the computing time without rewriting.
        print("\n" + "---------- Testing Phase ----------")
        runTests = input("Do you want to run tests? (y/n): ")
        if (runTests == 'y' or not runTests) and csvName == "UserData3.csv":
            tmp = 0
            execTimeList = []
            lineLimit = input("Insert amount of nodes on which the query should be applied at start (f.i. 100): ")
            if lineLimit:
                lineLimit = int(lineLimit)
            else:
                lineLimit = len(g.nodes)

            '''--- Non-EDP Query Test ---'''
            '''
                Query (I):   MATCH(n) RETURN count(n)
                Query (II):  MATCH(n)-[r]-() RETURN count(r)
                Query (III): MATCH(a: Person), (b: Person) WHERE a.age>63 AND a.name STARTS WITH 'A'
                             AND b.age>63 CREATE (a)-[r: NameASenior]->(b)
            '''
            # Evaluate computation time of non-edp queries
            runBlankQuery = input("Do you want to run the blank query? (y/n): ")

            if runBlankQuery == 'y':
                # Insert execution time in data set size steps increasing by 100 per iteration
                # can be set to 500000 max (UserData3.csv), because of performance issues mostly set to 40000
                while lineLimit <= int(oldLineLimit):
                    execTimeList.clear()
                    tmp = 0
                    # clear the graph before adding new nodes, adapt LIMIT value if not enough memory
                    while len(g.nodes) > 0:
                        print(
                            "Deleting Nodes: " + str(len(g.nodes)) + " and relations: " + str(len(g.relationships)))
                        g.run("MATCH(n) WITH n LIMIT 10000 DETACH DELETE n")

                    g.run("LOAD CSV WITH HEADERS FROM " + csvURL +
                          " AS line WITH line LIMIT " + str(lineLimit) + " CREATE (:Person "
                                                                         "{ name: line.name, gender: line.gender, age: toInteger(line.age), "
                                                                         "city: line.city, income: toFloat(line.income) })")

                    # Repeatedly Compute further commands if inserted above
                    if furtherInstr:
                        g.run(furtherInstr)

                    lineLimit += 100  # increase limit for loading more nodes and another query test
                    print("After commit")
                    print("Nodes: " + str(len(g.nodes)))
                    print("Relations: " + str(len(g.relationships)))

                    # Run every query 5 times and average the result, the first computation cannot be used
                    while tmp < 5:
                        # Measure execution time
                        blankQueryStart = time.time()

                        blankQuery = g.begin()
                        blankQuery.run(userQuery)
                        blankQuery.commit()

                        blankQueryEnd = time.time()
                        blankQueryTime = blankQueryEnd - blankQueryStart
                        print("Computation time of non-EDP query: " + str(blankQueryTime))

                        # Prevent the input of 0 seconds
                        if blankQueryTime != 0.0:
                            execTimeList.append(blankQueryTime)
                            tmp = tmp + 1

                    averagedTime = sum(execTimeList) / 5  # compute average of 5 measurements
                    print(averagedTime)

                    # Insert averaged execution time into NonEDPQueryEvaluation.csv for further evaluations
                    # Changed csv file name by hand for other query tests, name imply querying type and query
                    timeList = [lineLimit, str(len(g.relationships)), averagedTime]
                    with open('NonEDP-matchComplex.csv', 'a', newline='') as writeCSV:
                        print("Writing into "
                              "NonEDP-matchComplex.csv")
                        csvW = csv.writer(writeCSV, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        csvW.writerow(timeList)
                    writeCSV.close()

            ''' --- Query Rewriting Test --- '''
            runRewriting = input("Do you want to run query rewriting? (y/n): ")
            if runRewriting:
                utility = True  # set false if normal execution time test

                if userQuery == q1 and not utility:
                    pb = 10000  # set to very high level for convenience
                    while lineLimit <= int(oldLineLimit):
                        execTimeList.clear()
                        tmp = 0

                        # clear the graph before adding new nodes, adapt LIMIT value if not enough memory
                        while len(g.nodes) > 0:
                            print(
                                "Deleting Nodes: " + str(len(g.nodes)) + " and relations: " + str(
                                    len(g.relationships)))
                            g.run("MATCH(n) WITH n LIMIT 10000 DETACH DELETE n")

                        g.run("LOAD CSV WITH HEADERS FROM " + csvURL +
                              " AS line WITH line LIMIT " + str(lineLimit) + " CREATE (:Person "
                                                                             "{ name: line.name, gender: line.gender, age: toInteger(line.age), "
                                                                             "city: line.city, income: toFloat(line.income) })")

                        # Repeatedly Compute further commands if inserted above
                        if furtherInstr:
                            g.run(furtherInstr)

                        lineLimit += 100  # increase limit for loading more nodes and another query test

                        EDPQueryStart = time.time()  # start time measurement for anonymizing the query
                        # Reduce PB
                        # querying for unique identifiers is most sensitive and should never result in feasible output
                        if not "count" in userQuery:
                            print("Very sensitive")
                            pb = 0

                        print("Translating Cypher Query to be Epsilon-Differentially-Private")
                        # Check if query is a counting query - aggregation function and pb not exhausted
                        if "count" in userQuery and pb > 0:
                            print("Apply Sensitivity-Based Mechanism on Counting Query")
                            orig = g.begin()
                            saveOrig = next(
                                iter(orig.run(userQuery).data().pop().values()))  # Only label for test query
                            uniform = g.begin()
                            saveUniform = next(
                                iter(uniform.run("Match(n) return rand()-0.5 limit 1").data().pop().values()))
                            countQuery = g.begin()

                            # Applying Laplacian-Noise as locally sensitive method
                            countQuerySave = next(iter(countQuery.run(
                                "Match(n) return " + str(saveOrig) + "-(" + str(s) + "/" + str(eps) + ")*sign("
                                + str(saveUniform) + ")*log(1-2*abs(" + str(
                                    saveUniform) + ")) limit 1").data().pop().values()))
                            countQuery.commit()

                            pb = pb - int(s)  # Reduce Privacy Budget

                            EDPQueryEnd = time.time()
                            EDPQueryTime = EDPQueryEnd - EDPQueryStart
                            TotalCompTime = timeK + timeS + EDPQueryTime

                        # Write execution time of rewriting query (I) into csv
                        timeList = [str(len(g.nodes) + oldK), str(len(g.relationships)), oldK, s, eps, pb,
                                    TotalCompTime]
                        print(timeList)
                        with open('EDP_k_match_n_return_count_n.csv', 'a', newline='') as writeCSV:
                            print("Writing into csv")
                            csvW = csv.writer(writeCSV, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                            csvW.writerow(timeList)
                        writeCSV.close()

                elif userQuery == q1 and utility:
                    print("Utility Test")
                    saveOrig = saveOrig - oldK  # display the counting result no the original DB to measure dif
                    difResult = abs(saveOrig - countQuerySave)
                    timeList = [str(len(g.nodes)), oldK, s, eps, initPB, pb, saveOrig,
                                countQuerySave, difResult, TotalCompTime]
                    print(timeList)

                    with open('EDP_Utility_k_match_n_return_count_n.csv', 'a', newline='') as writeCSV:
                        print("Writing into csv")
                        csvW = csv.writer(writeCSV, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
                        csvW.writerow(timeList)
                    writeCSV.close()

                else:
                    print("Tests are only specified for the three query examples "
                          "described in the comments and the thesis.")

            else:
                print("Tests are currently only implemented for UserData3.csv")

    else:
        print("No Query was inserted.")
