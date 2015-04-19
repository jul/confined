=====================================================
Confined: a safe resource bound immutable interpreter
=====================================================

* source: https://github.com/jul/confined
* ticketing: https://github.com/jul/confined/issues

.. image:: 
   https://travis-ci.org/jul/confined.png

Use
===

The purpose of this interpreter is to confine the user in a predictable way
so that you don't have to fear to give your user the possibility to execute 
arbitrary code on your servers.

The language is mapping its input/internal stack to immutable data structures
so that remote it is safe to pass it 

Usage
=====

Example:

    print templatize(dict(
        price=1, 
        q=3, 
        vat=19.6, 
        name="super carcajou", country="FR"
    ),'''
    <:
    "hello":world
    :> ici <:
        $name
    :> has
    <:
        $price >NUM
        $q >NUM MUL
        $vat >NUM 100:_per_cent_to_per_one DIV 
        1:_having_price_AND_vat ADD MUL >STR
        " ":_separator
        CAT
        "comment in string and drop":_or_in_tag
        DROP
        "€":_cur "$":_cur 
        $country
        "FR":_cocorico
        1:_nb_of_lines_for_looking_match
        MATCH
        IFT
        CAT :>
    may I have a dict please? <:
        $price >NUM
        $q
        "a string":with_a_name
        "ignored":_because_tag_starts_with_
        1231231231231231:a_long_int
        "a new name":_with_space
        TAG
        EDICT
    :>  ....  
    <: "fin": :>
    end''')

Gives : 
    hello ici super carcajou has
    18.31 €
    may I have a dict please? {
        "q": "3", 
        "price": "1", 
        "with_a_name": "a string", 
        "a new name": "1231231231231231"
    }  ....  
    fin
    end


Changelog
=========

* 0.1.0 initial release oops forgot __name__ == main
* 0.1.1 initial release
* 0.1.2 going to fast, mis clicked a button in pypi
* 0.1.4 forgot howto declare requirements
* 0.1.9 after too many failure, embedding check_arg in this

Roadmap before 1.0.0
********************

* ensuring that stack is controled in size
* handle string in a nice way. I want ot be able to mix latin1/chinese in Input
* handle Decimal nitroglycerine correctly so that users CAN multiply safely
* Having a cheatsheet for the language
* create a loads/dumps to be able to serialize code from a user for remote
     execution
* limiting the size of the input scripts
* using only iterator to be able to do nth repeated operation without copying everything in memory
* handle versions compatibility for remote execution
* handle the precisions and formating of Decimal
* enough tests to feel secure
* python 3
