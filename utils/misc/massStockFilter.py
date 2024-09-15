from barcodeTierStockFilter import filter_products_by_stock

#just a cleaner looking file

if __name__ == "__main__":
    rexFile = './goodr_rex.csv'
    stockFile = './stock_data/apparel_data.csv'
    outputFile = './goodr_filtered.csv'

    filter_products_by_stock(product_file=rexFile, stock_file=stockFile, output_file=outputFile)
    