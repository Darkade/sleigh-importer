#!/bin/python3
"""Convert a CSV file to an Optaplanner XML file.
First step to solve the Santa's Sleigh Challenge
https://www.kaggle.com/c/santas-stolen-sleigh

This importer takes a CSV file and outputs an XML optaplanner file.

Created: Ivan Reyes, Alejandro Escobedo
December 18, 2015
"""


import xml.etree.ElementTree as ET
import csv
import argparse

class Consecutive:
    def __init__(self, initval = 0):
        self.i = initval

    def next(self):
        self.i += 1
        return str(self.i)

def get_params():
    """Gets parameters from terminal:

    - csv: a local CSV file to convert to XML
    - xml: the name of the output XML file."""

    parser = argparse.ArgumentParser(description='Charts an OptaPlanner <VrpTimeWindowedVehicleRoutingSolution> XML file.')

    parser.add_argument('csv', nargs=1, type=str, metavar='<CSV File>',
                        help='The CSV file to convert.')

    parser.add_argument('xml', nargs=1, type=str, metavar='<XML File>',
                        help='The <VrpTimeWindowedVehicleRoutingSolution> file to be created.')

    args = parser.parse_args()

    return {'csv': args.csv[0],
            'xml': args.xml[0]}

def get_gifts(inputfile):
    """Parses a gifts csv file as a list"""

    with open(inputfile, newline='') as csvfile:
        giftsreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        fl = True
        rows = []

        for row in giftsreader:
            if fl:
                fl = False
                continue
            rows.append(row)
    return rows

def _make_locations(gitft_list, topid):
    locations = ET.Element('locationList', id=topid.next())
    locationlist = []
    for gift in gitft_list:
        location = ET.Element('VrpAirLocation', id=topid.next())

        location_id = ET.SubElement (location, 'id')
        location_lat = ET.SubElement (location, 'latitude')
        location_lon = ET.SubElement (location, 'longitude')

        location_id.text = gift[0]
        location_lat.text = gift[1]
        location_lon.text = gift[2]

        locationlist.append(location)

    location = ET.Element('VrpAirLocation', id=topid.next())
    location_id = ET.SubElement (location, 'id')
    location_lat = ET.SubElement (location, 'latitude')
    location_lon = ET.SubElement (location, 'longitude')

    location_id.text = str(int(gift[0]) + 1)
    location_lat.text = '90.0'
    location_lon.text = '0.0'
    locationlist.append(location)

    locations.extend(locationlist)
    return locations, topid.i

def _make_customers(gift_list, topid):
    customers = ET.Element('customerList', id=topid.next())
    customerlist = []
    reference = 3

    for gift in gift_list:
        customer = ET.Element('VrpTimeWindowedCustomer', id=topid.next())

        customer_id = ET.SubElement (customer, 'id')
        customer_weight = ET.SubElement (customer, 'weight')

        attrib = {'reference': str(reference),
                  'clas': 'VrpAirLocation'}
        customer_location = ET.SubElement (customer, 'location',attrib=attrib)

        customer_id.text = gift[0]
        customer_weight.text = gift[3]

        customerlist.append(customer)

        reference +=1

    customers.extend(customerlist)
    return customers

def _make_depot(topid, reference):
    depots = ET.Element('depotList', id=topid.next())
    depot = ET.SubElement(depots, 'VrpTimeWindowedDepot', {'id': topid.next()})

    depot_id = ET.SubElement(depot, 'id')
    depot_id.text = '1'
    depot_location = ET.SubElement(depot, 'location', {'reference': str(reference)})

    return depots, topid.i

def _make_vehicles(topid, reference):
    vehicles = ET.Element('vehicleList', id=topid.next())
    vehicleList = []

    i = 1
    for vehicle in range(3):
        vehicle = ET.Element('VrpVehicle', id=topid.next())
        vehicle_id = ET.SubElement(vehicle, 'id')
        vehicle_wear = ET.SubElement(vehicle, 'wear')
        vehicle_depot = ET.SubElement(vehicle, 'depot', {'reference': str(reference)})

        vehicle_id.text = str(i)
        vehicle_wear = str(100)

        i +=1
        vehicleList.append(vehicle)

    vehicles.extend(vehicleList)
    return vehicles

def make_xml(gift_list):
    topid = Consecutive()
    solution = ET.Element('VrpTimeWindowedVehicleRoutingSolution', id=topid.next())

    locations, lref = _make_locations(gift_list, topid)
    customers = _make_customers(gift_list, topid)
    depots, dref = _make_depot(topid, lref)
    vehicles = _make_vehicles(topid, dref)

    solution.append(locations)
    solution.append(customers)
    solution.append(depots)
    solution.append(vehicles)

    return solution

def main():
    params = get_params()

    gift_list = get_gifts(params['csv'])
    solution = make_xml(gift_list)

    ET.ElementTree(solution).write(params['xml'])

main()
