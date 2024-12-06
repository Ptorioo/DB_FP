def search_article():
    keyword = input("Enter keyword: ").strip()

    if keyword:
        return keyword
    else:
        print("Keyword can't be empty.")