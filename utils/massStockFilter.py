from barcodeTierStockFilter import filter_products_by_stock



if __name__ == "__main__":
    rexFile = './data/22_23_run_rem.csv'
    stockFile = './stock_data/footwear_data.csv'
    outputFile = './22_23_run_rem_stock_filtered.csv'

    filter_products_by_stock(product_file=rexFile, stock_file=stockFile, output_file=outputFile)
    