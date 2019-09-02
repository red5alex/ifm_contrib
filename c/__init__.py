import ifm

def closeAllDocuments():
    """
    Close all open documents

    :return:
    """
    while ifm.getNumberOfDocuments() > 0:
        ifm.getDocument(0).closeDocument()