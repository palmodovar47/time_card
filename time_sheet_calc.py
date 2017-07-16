"""
calcs a timesheet json array
"""
import json
import csv
from copy import deepcopy
from datetime import datetime
from tabulate import tabulate

def group_items(time_sheet):
    """
    group items
    """

    def get_work_time_objs_via_item_num(time_sheet, item_num):
        """
        returns a list of dictionaries that have a given item number
        within them
        """
        result = []
        for item in time_sheet:
            if item['item'] == item_num:
                result.append(item)
        return result

    new_sheet = {}
    temp_items = []

    for i in time_sheet:
        temp_items.append(i['item'])

    set_of_item_nums = set(temp_items)

    for item_num in set_of_item_nums:
        new_sheet[str(item_num)] = get_work_time_objs_via_item_num(
            time_sheet, item_num)

    for work_item_group in new_sheet:
        for work_item in new_sheet[work_item_group]:
            del work_item['item']

    return new_sheet



def group_sub_items(time_sheet):
    """
    group sub items
    """

    for work_item_group_id in time_sheet:

        sub_item_ids = []
        temp = {}
        working_branch = time_sheet[work_item_group_id]

        for obj in working_branch:
            sub_item_ids.append(obj['subItemId'])

        sub_item_id_set = set(sub_item_ids)

        for unique_sub_item_id in sub_item_id_set:
            temp[str(unique_sub_item_id)] = []
            temp_branch = temp[str(unique_sub_item_id)]

            for obj in working_branch:
                if obj['subItemId'] == unique_sub_item_id:
                    temp_branch.append(dict(obj))

            for obj in temp_branch:
                del obj['subItemId']

        time_sheet[work_item_group_id] = deepcopy(temp)

    return time_sheet

def in_out_to_hours(time_sheet):
    """
    gets the difference between the time in and the time out
    """
    billable_time = None
    for work_item in time_sheet:
        for sub_work_item in time_sheet[work_item]:
            for idx, obj in enumerate(time_sheet[work_item][sub_work_item]):
                temp = deepcopy(obj)
                time_in = datetime.strptime(obj['timeIn'], "%H%M")
                time_out = datetime.strptime(obj['timeOut'], "%H%M")
                billable_time = time_out - time_in
                seconds = billable_time.seconds
                minutes = seconds/60
                hours = round(minutes/60, 2)
                temp['hoursWorked'] = deepcopy(hours)
                time_sheet[work_item][sub_work_item][idx] = temp

    return time_sheet

def time_worked_for_sub_item(time_sheet, work_item_nm='', sub_work_item_nm=''):
    """
    takes a time_sheet, work item number, and a sub work item number and returns
    the total hours worked for that sub-item
    """
    result = 0.00
    for work_time_obj in time_sheet[work_item_nm][sub_work_item_nm]:
        result += work_time_obj['hoursWorked']
    return result

def time_worked_for_item(time_sheet, work_item_nm=''):
    """
    takes a time_sheet and a work item number and returns
    the total hours worked for that item
    """
    result = 0.00
    for sub_work_item_nm in time_sheet[work_item_nm]:
        result += time_worked_for_sub_item(
            time_sheet, work_item_nm, sub_work_item_nm
        )
    return result

def time_worked_for_time_sheet(time_sheet):
    """
    takes a timesheet and returns the total hours worked
    """
    result = 0.00
    for work_item_nm in time_sheet:
        result += time_worked_for_item(
            time_sheet, work_item_nm
        )
    return result

def money_for_sheet(time_sheet):
    """
    calcs the total amount of money owed for the entire sheet
    """
    result = 0.00
    for i in time_sheet:
        for sub_i in time_sheet[i]:
            for work_obj in time_sheet[i][sub_i]:
                result += work_obj['rate'] * work_obj['hoursWorked']
    return result



def tabulate_helper(time_sheet):
    """
    tabulate_helper
    """

    def add_slashes(date_string):
        """
        adds slashes to a date string
        """
        date = date_string
        date = date[:2] + '/' + date[2:4] + '/' + date[4:]
        return date

    def insert_colon(mil_time):
        """
        adds a colon after the first two chars in a string
        """
        return mil_time[:2] + ':' + mil_time[2:]

    def format_money(amount):
        """
        adds a dollar sign to the front of the string
        """
        if isinstance(amount, float):
            return '$' + str(amount)
        else:
            return '$' + str(amount) + '.00'

    def export_sub_item(work_obj_as_list):
        """
        returns the sub item id in a work_obj_as_list
        """
        return work_obj_as_list[1]

    def export_work_item(work_obj_as_list):
        """
        returns the work item id of the work_obj_as_list
        """
        return work_obj_as_list[0]

    top_list = []
    for work_item_id in time_sheet:
        for sub_item_id in time_sheet[work_item_id]:
            for obj in time_sheet[work_item_id][sub_item_id]:
                work_item_temp_list = []
                work_item_temp_list.append(str(work_item_id))
                work_item_temp_list.append(str(sub_item_id))
                work_item_temp_list.append(str(obj['comment']))
                work_item_temp_list.append(str(obj['hoursWorked']))
                work_item_temp_list.append(format_money(obj['rate']))
                work_item_temp_list.append(add_slashes(str(obj['dateIn'])))
                work_item_temp_list.append(insert_colon(str(obj['timeIn'])))
                work_item_temp_list.append(insert_colon(str(obj['timeOut'])))
                top_list.append(work_item_temp_list)
    top_list = sorted(top_list, key=export_sub_item)
    top_list = sorted(top_list, key=export_work_item)
    return top_list

def print_tabular_form(time_sheet):
    """
    pretty prints the time sheet
    """
    headers = [
        'Item',
        'Sub-Item',
        'comment',
        'Billable Hours',
        'Rate',
        'Date',
        'Start',
        'End'
    ]
    data = tabulate_helper(time_sheet)
    return tabulate(data, headers=headers)

# def save_as_csv(time_sheet):
#     """
#     saves the tabulated form of the timesheet in csv form
#     """
#     time_sheet = tabulate_helper(time_sheet)
#     new_csv = csv.reader(time_sheet)
#     csv
#     with open('timeSheet.csv', mode='w') as csv_f:
        


def print_as_json(time_sheet):
    """
    pretty prints the time_sheet
    """
    print(json.dumps(time_sheet, indent=4, sort_keys=True))

def save_as_json(time_sheet):
    """
    saves the output of "print_as_json" as a .json file.
    """
    with open('groupedTimeSheet.json', mode='w') as f:
        json.dump(time_sheet, f, indent=4, sort_keys=True)

def main():
    """
    The program entry point
    """
    time_file = open('timeSheet.json')
    time_sheet = json.load(time_file)
    time_file.close()

    time_sheet = group_items(time_sheet)
    time_sheet = group_sub_items(time_sheet)
    time_sheet = in_out_to_hours(time_sheet)

    total = time_worked_for_time_sheet(time_sheet)
    total_money = money_for_sheet(time_sheet)

    print_as_json(time_sheet)
    print(print_tabular_form(time_sheet))
    print('total hours worked so far:', total, 'Dollar amount due: $' + str(total_money))

if __name__ == '__main__':
    main()
