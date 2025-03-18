from forestfire.database.connection import connect_to_db, close_connection



def fetch_picklist_data(connection=connect_to_db()):
    """Fetch required picklist data"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO nifiapp;")
            cursor.execute("SELECT * FROM picklist;")
            return cursor.fetchall()
    finally:
        close_connection(connection)

def fetch_distinct_picktasks(connection=connect_to_db()):
    """Fetch distinct picktask IDs"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SET search_path TO nifiapp;")
            cursor.execute("SELECT DISTINCT picktaskid FROM picklist;")
            return cursor.fetchall()
    finally:
        close_connection(connection)


def mapping(rows,picktasks):
    result = {}

    fetch_picklist_data()
    fetch_distinct_picktasks()


    result = {}
    stage_result={}

    for picktask_tuple in picktasks:
        picktaskid = picktask_tuple[0] 
        
        filtered_values = [
            (row[21], row[22]) 
            for row in rows
            if row[3] == picktaskid
        ]

        staging_loc = [
            (row[67], row[68]) 
            for row in rows
            if row[3] == picktaskid
        ]

        
        if picktaskid in result:
            result[picktaskid].extend(filtered_values) 
        else:
            result[picktaskid] = filtered_values

        stage_result[picktaskid] = staging_loc
    return stage_result,result

def getdata():

    staging,taskid= mapping()

    return taskid.keys(), [[item] for sublist in taskid.values() for item in sublist],staging  #order assign
