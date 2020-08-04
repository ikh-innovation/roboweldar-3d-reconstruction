import pyfiware

def scratch():
    oc = pyfiware.OrionConnector("http://127.0.0.1:1026")
    print(oc)

    result = oc.count()
    result = oc.get("123")

    # create service

    result = oc.create()

    print(result)


if __name__ == '__main__':
    main()