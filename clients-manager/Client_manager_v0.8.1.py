import json

currency = ''
currency2 = ''

def jsonDump():
    with open('clients.json', 'w', encoding='utf-8') as file0:
        return json.dump(clientList, file0, ensure_ascii=False, indent=4)

def cur():
    global currency, currency2
    try:
        currency = input('Сhoose your currency (usd, eur, rub)\n~ ').lower()
        if currency == 'usd':
            currency = '$'
            currency2 = ''
        elif currency == 'eur':
            currency = '€'
            currency2 = ''
        elif currency == 'rub':
            currency = ''
            currency2 = '₽'
        else:
            currency = ''
            currency2 = ''
        return currency, currency2
    except KeyboardInterrupt:
        print('You\'ve exit')


a = '\nChoose a suitable <ID>\n<1> Choise currency\n<2> Show clients\n<3> Add client\n<4> Find client\n<5> Delete client\n<6> Edit client (amount)\n<7> Statistic\n<8> Exit'
print('\nChoose a suitable <ID>\n<1> Choise currency\n<2> Show clients\n<3> Add client\n<4> Find client\n<5> Delete client\n<6> Edit client (amount)\n<7> Statistic\n<8> Exit\nUse /help to show the table')
def load_clients():
    try:
        with open('clients.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        return []

clientList = load_clients()

def clients():
    print('\n[Clients]')
    global currency, currency2
    try:
        with open('clients.json', 'r', encoding='utf-8') as file:
            users = json.load(file)
            for x in users:
                print(f'{x["name"]} - {currency if currency else ""}{x["amount"]}{currency2}')
            return
    except (json.decoder.JSONDecodeError, FileNotFoundError):
        print('\nList empty...')

def add():
    try:
        while True:

            try:
                client = input('\n[Add new client]\nEnter name\n~ ').title()
                if not client:
                    break
            except ValueError as e:
                print(f'Error: {e}\n*Name must be a word')
                continue

            try:
                amount = float(input('Enter amount\n~ '))
                if not amount:
                    break
            except ValueError as e:
                print(f'Error: {e}\n*Amount must be a number')
                continue

            new_clients = {
                'name': client,
                'amount': amount
            }

            clientList.append(new_clients)

            jsonDump()

            user = input('Keep add client? (y/n)\n~ ')
            if user != 'y':
                return
    except KeyboardInterrupt:
        print('You\'ve exit')

def find(value):
    if not value:
        return
    else:
       with open('clients.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            for x in data:
                if x['name'] == value:
                    print(f'{x['name']} - {currency if currency else ""}{x['amount']}{currency2}')
                    return
            print('Empty...')

def delete(delClient):
    clientList = []
    found = False
    try:
        with open('clients.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        for x in data:
            if x['name'] != delClient:
                clientList.append(x)
            else:
                found = True
        with open('clients.json', 'w', encoding='utf-8') as file0:
            json.dump(clientList, file0, ensure_ascii=False, indent=4)
        if found:
            return print(f'Client {delClient.title()} deleted')
        else:
            return print(f'Client {delClient} not found')
    except (KeyboardInterrupt, KeyError) as e:
        print(f'Error: {e}')
    except FileNotFoundError:
        print('clients.json не найден')
    except json.JSONDecodeError:
        print('Файл clients.json не является корректным JSON')

def editClient(client, amount):
    found = False
    clientList = []
    if client and amount:
        with open('clients.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        for x in data:
            if x['name'] != client:
                clientList.append(x)
            else:
                found = True
                x['amount'] = amount
                clientList.append(x)
        with open('clients.json', 'w', encoding='utf-8') as file2:
            json.dump(clientList, file2, ensure_ascii=False, indent=4)
        if found:
            print(f'{client.title()} been edited')
        else:
            print(f'client {client} not found')
    else:
        print('Enter the value or exit <8>')
        return

def statistic():
    try:
        tAmount = 0
        averageAmount = 0
        print('\n[Statistic]')
        with open('clients.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
        print(f'Clients: {len(data)}')
        a = len(data)
        for x in data:
            tAmount += x['amount']
        print(f'Total amount: {currency}{tAmount}{currency2}')
        averageAmount = tAmount / a
        print(f'Average amount: {averageAmount}')
        biggestAm = 0
        biggestClient = None
        for x in data:
            if x['amount'] > biggestAm:
                biggestClient = x['name']
                biggestAm = x['amount']
        print(f'Biggest client: {biggestClient} - {currency}{biggestAm}{currency2}')
    except (ZeroDivisionError, FileNotFoundError, json.JSONDecodeError) as e:
        print(f'Error: {e}')
        return

def menu(value):
    try:
        if value == '/help':
            print(a)
        elif value == '1':
            cur()
        elif value == '2':
            clients()
        elif value == '3':
            add()
        elif value == '4':
            find(input('\n[Search client]\nEnter client name\n~ ').title())
        elif value == '5':
            delete(input('\n[Delete client]\nEnter client name\n~ ').title())
        elif value == '6':
            editClient(input('\n[Edit client]\nEnter name\n~ ').title(), float(input('Enter amount\n~ ')))
        elif value == '7':
            statistic()
        elif value == '8':
            return print('Try again')
        else:
            print('Invalid value\nEnter <8> to exit')
    except KeyboardInterrupt:
        print('You\'ve exit')
menu(input('\n<ID>~ '))

while True:
    try:
        choise = input('\n<ID>~ ')
        if choise == '8':
            print('You\'ve exit')
            break
        menu(choise)
    except KeyboardInterrupt:
        print('Enter <8> to exit')