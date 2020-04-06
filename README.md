# XRCC_RestAPI
## Installation
1. Make sure you have virtualenv installed on your system:

  ```
  pip install virtualenv
  ```
        
2. Clone this repo to a desired directory with:

  ```
  git clone https://github.com/Geodude25trade/XRCC_RestAPI/
  ```
      
3. Setup a virtual environment inside the same directory with:

  ```
  python -m virtualenv env
  ```
      
4. Activate the virtual environment with:
    #### __Windows__
      ```
      env\Scripts\activate.bat
      ```
    #### __Linux__
      ```
      source env/bin/activate
      ```
5. Run the setup.py in the project to install all of the dependencies using

  ```
  python setup.py
  ```
## Starting the Server
1. To start the server, type the following command while the virtual environment is active:

  ```
  waitress-serve --call app:create_app
  ```

  _The server may take several minutes to start up and even longer if the word2vec model has not yet been downloaded_
## Interacting with the server
  To interact with the server, use either Postman or some equivalent to POST JSON objects to the various routes. The format of each object and its associated route is outlined below.
  
```JSON
{
  "algorithm": "[empath | wfc | chi-squared]",
  "username": "[twitter handle]",
  "newTweets": [bool; true if force new tweet scrape],
  "numTweets": [int; number of tweets to fetch],
  "numInterests": [int; number of interests to return]
}
```

```JSON
{
  "algorithm": "[empath | wfc | chi-squared]",
  "user1": "[twitter handle]",
  "user2": "[twitter handle]",
  "newTweets": [bool; true if force new tweet scrape],
  "numTweets": [int; number of tweets to fetch],
  "numInterests": [int; number of interests to return]
}

```JSON
{
  "word": "[The word to find closest emojis to]",
  "number": [int; number of closest to return]
}
```

```JSON
{
  "emoji": "[name of the emoji to return a png for]"
}
```
