This application extract all transactions data from hmi.mrud.ir into a csv file. It is implemented in Python.

How to install
=========

```
python3 -m venv venv/
source venv/bin/activate
pip3 install -r requirements.txt
python3 main.py
```

How to use
=========

```
source venv/bin/activate
python3 main.py
```

TODO
=========

  * Implement update monthly transactions for this month
  * Implementing a mechanism to generate logs on each run
  * Fix data formats to be readable by MySQL
  * Implement a mechanism for renewing session in robots settings
  * Add mortgage field to the result table
  * Implement connection to MySQL and write the results in the specific Codeigniter's table
  * Write queries and design charts from extracted data with semantic value
