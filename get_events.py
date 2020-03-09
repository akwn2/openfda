import requests
import pandas as pd

# API key
api_key = 'HSxEALnHT6zavIQJFJAr3LqYtUFxyZUKrZodx05L'


def parse_data(data):
    """
    Parses the data in table format while extracting the information relevant
    to the analysis conducted and returns the encodings used.

    :param data: JSON results from API query
    :return: Pandas DataFrame with the key variables analysed
    """
    N = len(data)
    table = list()

    drug_dict = dict()
    inv_drug_dict = dict()
    drug_uid = 0

    manufacturer_dict = dict()
    inv_manufacturer_dict = dict()
    manufacturer_uid = 0

    country_dict = dict()
    inv_country_dict = dict()
    country_uid = 0

    reaction_dict = dict()
    inv_reaction_dict = dict()
    reaction_uid = 0

    for patient_id in range(N):

        # Patient information
        try:
            age = int(data[patient_id]['patient']['patientonsetage'])
            if age > 150:
                raise ValueError  # Clearly a mistake in the FDA database

            sex = int(data[patient_id]['patient']['patientsex'])

            # Country codes
            #fixme: There is plent of repetition in the code, and should be removed for better maintainability.
            country = data[patient_id]['occurcountry']
            if country not in country_dict.keys():
                country_dict[country] = country_uid
                inv_country_dict[country_uid] = country
                country_uid += 1

            country = country_dict[country]
            
            # Type of primary source
            source = int(data[patient_id]['primarysource']['qualification'])
            
            # Seriousness
            seriousness = int(data[patient_id]['serious'])

            if 'seriousnessdeath' in data[patient_id].keys():
                death = 1
            else:
                death = 0

            if 'seriousnessdisabling' in data[patient_id].keys():
                disabling = 1
            else:
                disabling = 0

            if 'seriousnesslifethreatening' in data[patient_id].keys():
                life_threatening = 1
            else:
                life_threatening = 0

            if 'seriousnesshospitalization' in data[patient_id].keys():
                hospitalization = 1
            else:
                hospitalization = 0

            if 'seriousnessother' in data[patient_id].keys():
                serious_other = 1
            else:
                serious_other = 0

            # Information for each drug the patient was administered
            n_drugs = len(data[patient_id]['patient']['drug'])

            for dd in range(n_drugs):
                drug = data[patient_id]['patient']['drug'][dd]['openfda']['generic_name']

                # Let's be extra careful in not assigning duplicates if the generic name of the drug
                # is given in different order for different entries, e.g.
                # ['OXIGEN', 'AIR'] in one case and ['AIR', 'OXIGEN'] in another
                new_drug = False
                for entry in drug:
                    if entry not in drug_dict.keys():
                        drug_dict[entry] = drug_uid
                        new_drug = True

                if new_drug:
                    inv_drug_dict[drug_uid] = drug
                    drug_uid += 1

                drug = drug_dict[entry]

                # Manufacturer information
                # We will assume that manufacturers will always have the same encoding in the FDA database.
                manufacturer = data[patient_id]['patient']['drug'][dd]['openfda']['manufacturer_name'][0]

                # Compile a list of manufactures and use a unique identifier for each
                if manufacturer not in manufacturer_dict.keys():
                    manufacturer_dict[manufacturer] = manufacturer_uid
                    inv_manufacturer_dict[manufacturer_uid] = manufacturer
                    manufacturer_uid += 1

                manufacturer = manufacturer_dict[manufacturer]

                # Information for each adverse reaction reported
                n_reactions = len(data[patient_id]['patient']['reaction'])
                for react in range(n_reactions):
                    reaction = data[patient_id]['patient']['reaction'][react]['reactionmeddrapt']
                    if reaction not in reaction_dict.keys():
                        reaction_dict[reaction] = reaction_uid
                        inv_reaction_dict[reaction_uid] = reaction
                        reaction_uid += 1

                    reaction = reaction_dict[reaction]

                    outcome = int(data[patient_id]['patient']['reaction'][react]['reactionoutcome'])

                    table.append([patient_id, age, sex, country, source, seriousness,
                                  death, disabling, life_threatening, hospitalization,
                                  serious_other, drug, manufacturer, reaction, outcome])
        except:
            pass  #fixme: We'll just exclude missing information, but would need to think about this in a real life case

    # Output the map from unique identifiers to results
    encodings = {
        'country': inv_country_dict,
        'drug': inv_drug_dict,
        'manufacturers': inv_manufacturer_dict,
        'reaction': inv_reaction_dict,
    }

    table = pd.DataFrame(table, columns=['Patient', 'Age', 'Sex', 'Country', 'Source', 'Seriousness',
                                         'Death', 'Disabling', 'Life Threatening', 'Hospitalization',
                                         'Other serious', 'Drug', 'Manufacturer', 'Reaction', 'Outcome'])

    return table, encodings


def get_data(search_param=None, count_param=None, require_param=None, limit_param=None,
             start='20040101', end='20170731'):
    """
    executes a query on the FDA API.
    :param search_param: search
    :param count_param: counting by
    :param require: require existence of fields. By default requieres the patient information w.r.t.
                                         'Age', 'Sex', 'Country', 'Seriousness'.
    :param limit: limiting records
    :param start: start date
    :param end: end date
    :return: JSON results
    """
    # Parse date
    date_limits = 'receivedate:[' + start + '+TO+' + end + ']'

    # Parse counting parameter
    if count_param is None:
        count = ''
    else:
        count = '&count=' + count_param

    # Include default required fields to minimize missing data
    if require_param is None:
        require = '+AND+'
        require += '_exists_:patient.patientonsetage+AND+'
        require += 'patient.patientonsetageunit:801+AND+'  # Age in years
        require += '_exists_:patient.patientsex+AND+'
        require += '_exists_:occurcountry+AND+'
        require += '_exists_:serious+AND+'

    # Parse search
    if search_param is None:
        search = '&search=' + require + date_limits
    else:
        search = '&search=' + date_limits + '+AND+' + search_param

    # Find a way around the limitations of the query
    if limit_param is None:
        limit = ''
        skip = ''
    else:
        limit = '&limit=100'
        skip = '&skip='

    # Here we append all results to a table to get around limitations in the query.
    #fixme: in the future, make this more understandable
    results = list()
    for page in range(int(limit_param / 100)):
        url = 'https://api.fda.gov/drug/event.json?api_key=' + \
              api_key + search + count + limit + skip + str(100 * page)

        data = requests.get(url).json()
        if len(results) > 0:
            for index in range(len(data['results'])):
                results.append(data['results'][index])
        else:
            results = data['results']

    return results


if __name__ is '__main__':
    # fixme: include proper unit tests later.
    # A simple case to check if the output is sensible
    search = 'patient.drug.drugindication:hypertension'
    data = get_data(search, limit_param=1000)
    data, encodings = parse_data(data)
    print(data)
