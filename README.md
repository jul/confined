# confined
a confined interpreter that will be easy to tweak for your needs.


#Example

##template

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

#OUTPUT 0

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




##INPUT 1
    +1.23:exist +12:int "AZE":a_string +123:a_number $a $b >NUM SWAP 
    "a_string":_key GET "a":another_key
    "toto":_miss_get GET CAT "data":_tag TAG  TOP
    1:thos 1.2:notavala 3:val 1:_totest 3:sizeo_compare MATCH IFT "FUN":_str
    "SWAP,EJOIN":test_eval EVAL "toto":AZE 

##OUTPUT 1



    BEFORE APPLYING 6, >NUM
    ******************************************
    |   5 | <Val:type='num' val=1.23 tag='exist'>
    |   4 | <Val:type='num' val=12 tag='int'>
    |   3 | <Val:type='str' val=AZE tag='a_string'>
    |   2 | <Val:type='num' val=123 tag='a_number'>
    |   1 | <Val:type='str' val=1 tag='a'>
    |   0 | <Val:type='str' val=2 tag='b'>
    ******************************************
    AFTER >NUM
    ******************************************
    |   5 | <Val:type='num' val=1.23 tag='exist'>
    |   4 | <Val:type='num' val=12 tag='int'>
    |   3 | <Val:type='str' val=AZE tag='a_string'>
    |   2 | <Val:type='num' val=123 tag='a_number'>
    |   1 | <Val:type='str' val=1 tag='a'>
    |   0 | <Val:type='num' val=2 tag='b'>
    ******************************************
    
    BEFORE APPLYING 7, SWAP
    ******************************************
    |   5 | <Val:type='num' val=1.23 tag='exist'>
    |   4 | <Val:type='num' val=12 tag='int'>
    |   3 | <Val:type='str' val=AZE tag='a_string'>
    |   2 | <Val:type='num' val=123 tag='a_number'>
    |   1 | <Val:type='str' val=1 tag='a'>
    |   0 | <Val:type='num' val=2 tag='b'>
    ******************************************
    AFTER SWAP
    ******************************************
    |   5 | <Val:type='num' val=1.23 tag='exist'>
    |   4 | <Val:type='num' val=12 tag='int'>
    |   3 | <Val:type='str' val=AZE tag='a_string'>
    |   2 | <Val:type='num' val=123 tag='a_number'>
    |   1 | <Val:type='num' val=2 tag='b'>
    |   0 | <Val:type='str' val=1 tag='a'>
    ******************************************
    
    BEFORE APPLYING 9, GET
    ******************************************
    |   6 | <Val:type='num' val=1.23 tag='exist'>
    |   5 | <Val:type='num' val=12 tag='int'>
    |   4 | <Val:type='str' val=AZE tag='a_string'>
    |   3 | <Val:type='num' val=123 tag='a_number'>
    |   2 | <Val:type='num' val=2 tag='b'>
    |   1 | <Val:type='str' val=1 tag='a'>
    |   0 | <Val:type='str' val=a_string tag='_key'>
    ******************************************
    ******************************************
    |   6 | <Val:type='num' val=1.23 tag='exist'>
    |   5 | <Val:type='num' val=12 tag='int'>
    |   4 | <Val:type='str' val=AZE tag='a_string'>
    |   3 | <Val:type='num' val=123 tag='a_number'>
    |   2 | <Val:type='num' val=2 tag='b'>
    |   1 | <Val:type='str' val=1 tag='a'>
    |   0 | <Val:type='num' val=4 tag='_findex'>
    ******************************************
    AFTER GET
    ******************************************
    |   5 | <Val:type='num' val=1.23 tag='exist'>
    |   4 | <Val:type='num' val=12 tag='int'>
    |   3 | <Val:type='num' val=123 tag='a_number'>
    |   2 | <Val:type='num' val=2 tag='b'>
    |   1 | <Val:type='str' val=1 tag='a'>
    |   0 | <Val:type='str' val=AZE tag='a_string'>
    ******************************************
    
    BEFORE APPLYING 12, GET
    ******************************************
    |   7 | <Val:type='num' val=1.23 tag='exist'>
    |   6 | <Val:type='num' val=12 tag='int'>
    |   5 | <Val:type='num' val=123 tag='a_number'>
    |   4 | <Val:type='num' val=2 tag='b'>
    |   3 | <Val:type='str' val=1 tag='a'>
    |   2 | <Val:type='str' val=AZE tag='a_string'>
    |   1 | <Val:type='str' val=a tag='another_key'>
    |   0 | <Val:type='str' val=toto tag='_miss_get'>
    ******************************************
    AFTER GET
    ******************************************
    |   6 | <Val:type='num' val=1.23 tag='exist'>
    |   5 | <Val:type='num' val=12 tag='int'>
    |   4 | <Val:type='num' val=123 tag='a_number'>
    |   3 | <Val:type='num' val=2 tag='b'>
    |   2 | <Val:type='str' val=1 tag='a'>
    |   1 | <Val:type='str' val=AZE tag='a_string'>
    |   0 | <Val:type='str' val=a tag='another_key'>
    ******************************************
    
    BEFORE APPLYING 13, CAT
    ******************************************
    |   6 | <Val:type='num' val=1.23 tag='exist'>
    |   5 | <Val:type='num' val=12 tag='int'>
    |   4 | <Val:type='num' val=123 tag='a_number'>
    |   3 | <Val:type='num' val=2 tag='b'>
    |   2 | <Val:type='str' val=1 tag='a'>
    |   1 | <Val:type='str' val=AZE tag='a_string'>
    |   0 | <Val:type='str' val=a tag='another_key'>
    ******************************************
    AFTER CAT
    ******************************************
    |   5 | <Val:type='num' val=1.23 tag='exist'>
    |   4 | <Val:type='num' val=12 tag='int'>
    |   3 | <Val:type='num' val=123 tag='a_number'>
    |   2 | <Val:type='num' val=2 tag='b'>
    |   1 | <Val:type='str' val=1 tag='a'>
    |   0 | <Val:type='str' val=aAZE tag=''>
    ******************************************
    
    BEFORE APPLYING 15, TAG
    ******************************************
    |   6 | <Val:type='num' val=1.23 tag='exist'>
    |   5 | <Val:type='num' val=12 tag='int'>
    |   4 | <Val:type='num' val=123 tag='a_number'>
    |   3 | <Val:type='num' val=2 tag='b'>
    |   2 | <Val:type='str' val=1 tag='a'>
    |   1 | <Val:type='str' val=aAZE tag=''>
    |   0 | <Val:type='str' val=data tag='_tag'>
    ******************************************
    AFTER TAG
    ******************************************
    |   5 | <Val:type='num' val=1.23 tag='exist'>
    |   4 | <Val:type='num' val=12 tag='int'>
    |   3 | <Val:type='num' val=123 tag='a_number'>
    |   2 | <Val:type='num' val=2 tag='b'>
    |   1 | <Val:type='str' val=1 tag='a'>
    |   0 | <Val:type='str' val=aAZE tag='data'>
    ******************************************
    
    BEFORE APPLYING 16, TOP
    ******************************************
    |   5 | <Val:type='num' val=1.23 tag='exist'>
    |   4 | <Val:type='num' val=12 tag='int'>
    |   3 | <Val:type='num' val=123 tag='a_number'>
    |   2 | <Val:type='num' val=2 tag='b'>
    |   1 | <Val:type='str' val=1 tag='a'>
    |   0 | <Val:type='str' val=aAZE tag='data'>
    ******************************************
    AFTER TOP
    ******************************************
    |   5 | <Val:type='str' val=aAZE tag='data'>
    |   4 | <Val:type='num' val=1.23 tag='exist'>
    |   3 | <Val:type='num' val=12 tag='int'>
    |   2 | <Val:type='num' val=123 tag='a_number'>
    |   1 | <Val:type='num' val=2 tag='b'>
    |   0 | <Val:type='str' val=1 tag='a'>
    ******************************************
    
    BEFORE APPLYING 22, MATCH
    ******************************************
    |  10 | <Val:type='str' val=aAZE tag='data'>
    |   9 | <Val:type='num' val=1.23 tag='exist'>
    |   8 | <Val:type='num' val=12 tag='int'>
    |   7 | <Val:type='num' val=123 tag='a_number'>
    |   6 | <Val:type='num' val=2 tag='b'>
    |   5 | <Val:type='str' val=1 tag='a'>
    |   4 | <Val:type='num' val=1 tag='thos'>
    |   3 | <Val:type='num' val=1.2 tag='notavala'>
    |   2 | <Val:type='num' val=3 tag='val'>
    |   1 | <Val:type='num' val=1 tag='_totest'>
    |   0 | <Val:type='num' val=3 tag='sizeo_compare'>
    ******************************************
    AFTER MATCH
    ******************************************
    |   6 | <Val:type='str' val=aAZE tag='data'>
    |   5 | <Val:type='num' val=1.23 tag='exist'>
    |   4 | <Val:type='num' val=12 tag='int'>
    |   3 | <Val:type='num' val=123 tag='a_number'>
    |   2 | <Val:type='num' val=2 tag='b'>
    |   1 | <Val:type='str' val=1 tag='a'>
    |   0 | <Val:type='num' val=1 tag='_matches'>
    ******************************************
    
    BEFORE APPLYING 23, IFT
    ******************************************
    |   6 | <Val:type='str' val=aAZE tag='data'>
    |   5 | <Val:type='num' val=1.23 tag='exist'>
    |   4 | <Val:type='num' val=12 tag='int'>
    |   3 | <Val:type='num' val=123 tag='a_number'>
    |   2 | <Val:type='num' val=2 tag='b'>
    |   1 | <Val:type='str' val=1 tag='a'>
    |   0 | <Val:type='num' val=1 tag='_matches'>
    ******************************************
    AFTER IFT
    ******************************************
    |   4 | <Val:type='str' val=aAZE tag='data'>
    |   3 | <Val:type='num' val=1.23 tag='exist'>
    |   2 | <Val:type='num' val=12 tag='int'>
    |   1 | <Val:type='num' val=123 tag='a_number'>
    |   0 | <Val:type='num' val=2 tag='b'>
    ******************************************
    
    BEFORE APPLYING 26, EVAL
    ******************************************
    |   6 | <Val:type='str' val=aAZE tag='data'>
    |   5 | <Val:type='num' val=1.23 tag='exist'>
    |   4 | <Val:type='num' val=12 tag='int'>
    |   3 | <Val:type='num' val=123 tag='a_number'>
    |   2 | <Val:type='num' val=2 tag='b'>
    |   1 | <Val:type='str' val=FUN tag='_str'>
    |   0 | <Val:type='str' val=SWAP,EJOIN tag='test_eval'>
    ******************************************
    BEFORE APPLYING 0, SWAP
    ******************************************
    |   5 | <Val:type='str' val=aAZE tag='data'>
    |   4 | <Val:type='num' val=1.23 tag='exist'>
    |   3 | <Val:type='num' val=12 tag='int'>
    |   2 | <Val:type='num' val=123 tag='a_number'>
    |   1 | <Val:type='num' val=2 tag='b'>
    |   0 | <Val:type='str' val=FUN tag='_str'>
    ******************************************
    AFTER SWAP
    ******************************************
    |   5 | <Val:type='str' val=aAZE tag='data'>
    |   4 | <Val:type='num' val=1.23 tag='exist'>
    |   3 | <Val:type='num' val=12 tag='int'>
    |   2 | <Val:type='num' val=123 tag='a_number'>
    |   1 | <Val:type='str' val=FUN tag='_str'>
    |   0 | <Val:type='num' val=2 tag='b'>
    ******************************************
    
    BEFORE APPLYING 1, EJOIN
    ******************************************
    |   5 | <Val:type='str' val=aAZE tag='data'>
    |   4 | <Val:type='num' val=1.23 tag='exist'>
    |   3 | <Val:type='num' val=12 tag='int'>
    |   2 | <Val:type='num' val=123 tag='a_number'>
    |   1 | <Val:type='str' val=FUN tag='_str'>
    |   0 | <Val:type='num' val=2 tag='b'>
    ******************************************
    EXITING
    AFTER EJOIN
    ******************************************
    |   7 | <Val:type='str' val=aAZE tag='data'>
    |   6 | <Val:type='num' val=1.23 tag='exist'>
    |   5 | <Val:type='num' val=12 tag='int'>
    |   4 | <Val:type='num' val=123 tag='a_number'>
    |   3 | <Val:type='str' val=FUN tag='_str'>
    |   2 | <Val:type='num' val=2 tag='b'>
    |   1 | 'data=aAZE&exist=1.23&int=12&a_number=123&b=2'
    |   0 | '<<TERM>>'
    ******************************************
    
    ******************************************
    |   7 | <Val:type='str' val=aAZE tag='data'>
    |   6 | <Val:type='num' val=1.23 tag='exist'>
    |   5 | <Val:type='num' val=12 tag='int'>
    |   4 | <Val:type='num' val=123 tag='a_number'>
    |   3 | <Val:type='str' val=FUN tag='_str'>
    |   2 | <Val:type='num' val=2 tag='b'>
    |   1 | 'data=aAZE&exist=1.23&int=12&a_number=123&b=2'
    |   0 | '<<TERM>>'
    ******************************************
    None
    ******************************************
    |   7 | <Val:type='str' val=aAZE tag='data'>
    |   6 | <Val:type='num' val=1.23 tag='exist'>
    |   5 | <Val:type='num' val=12 tag='int'>
    |   4 | <Val:type='num' val=123 tag='a_number'>
    |   3 | <Val:type='str' val=FUN tag='_str'>
    |   2 | <Val:type='num' val=2 tag='b'>
    |   1 | 'data=aAZE&exist=1.23&int=12&a_number=123&b=2'
    |   0 | '<<TERM>>'
    ******************************************
    AFTER EVAL
    ******************************************
    |   7 | <Val:type='str' val=aAZE tag='data'>
    |   6 | <Val:type='num' val=1.23 tag='exist'>
    |   5 | <Val:type='num' val=12 tag='int'>
    |   4 | <Val:type='num' val=123 tag='a_number'>
    |   3 | <Val:type='str' val=FUN tag='_str'>
    |   2 | <Val:type='num' val=2 tag='b'>
    |   1 | 'data=aAZE&exist=1.23&int=12&a_number=123&b=2'
    |   0 | '<<TERM>>'
    ******************************************
    
    ******************************************
    |   5 | <Val:type='str' val=aAZE tag='data'>
    |   4 | <Val:type='num' val=1.23 tag='exist'>
    |   3 | <Val:type='num' val=12 tag='int'>
    |   2 | <Val:type='num' val=123 tag='a_number'>
    |   1 | <Val:type='str' val=FUN tag='_str'>
    |   0 | <Val:type='num' val=2 tag='b'>
    ******************************************
    {
        "int": 12, 
        "exist": 1.23, 
        "data": "aAZE", 
        "a_number": 123
    }

    data=aAZE&exist=1.23&int=12&a_number=123&b=2
    
#INPUT 2

    +1.23:exist syntax_error_lololol +12:int "AZE":a_string +123:a_number $a $b >NUM SWAP 
    "a_string":_key GET "a":another_key
    "toto":_miss_get GET CAT "data":_tag TAG  TOP
    1:thos 1.2:notavala 3:val 1:_totest 3:sizeo_compare MATCH IFT "FUN":_str
    "SWAP,EJOIN:test_eval EVAL "toto":AZE 

#OUTPUT 2 
 
    **+1.23:exist syntax_error_lololol +12:int** "AZE":a_string +123:a_number $a $b >NUM SWAP 
    "a_string":_key GET "a":another_key
    "toto":_miss_get GET CAT "data":_tag TAG  TOP
    1:thos 1.2:notavala 3:val 1:_totest 3:sizeo_compare MATCH IFT "FUN":_str
    "SWAP,EJOIN:test_eval EVAL "toto":AZE 
    
    
    <+1.23:exist syntax_error_lololol +12:int> triggered EXCP Un parsed expression ** syntax_error_lololol ** in 
    
    +1.23:exist< syntax_error_lololol > "AZE":a_string +123:a_number $a $b >NUM SWAP 
    "a_string":_key GET "a":another_key
    "toto":_miss_get GET CAT "data":_tag TAG  TOP
    1:thos 1.2:notavala 3:val 1:_totest 3:sizeo_compare MATCH IFT "FUN":_str
    "SWAP,EJOIN:test_eval EVAL "toto":AZE 
    
    
    ******************************************
    |   6 | <Val:type='str' val=aAZE tag='data'>
    |   5 | <Val:type='num' val=1.23 tag='exist'>
    |   4 | <Val:type='num' val=12 tag='int'>
    |   3 | <Val:type='num' val=123 tag='a_number'>
    |   2 | <Val:type='str' val=FUN tag='_str'>
    |   1 | <Val:type='num' val=2 tag='b'>
    |   0 | <Val:type='num' val=1.23 tag='exist'>
    ******************************************
    None
    ******************************************
    |   6 | <Val:type='str' val=aAZE tag='data'>
    |   5 | <Val:type='num' val=1.23 tag='exist'>
    |   4 | <Val:type='num' val=12 tag='int'>
    |   3 | <Val:type='num' val=123 tag='a_number'>
    |   2 | <Val:type='str' val=FUN tag='_str'>
    |   1 | <Val:type='num' val=2 tag='b'>
    |   0 | <Val:type='num' val=1.23 tag='exist'>
    ******************************************
    [<Val:type='str' val=aAZE tag='data'>, <Val:type='num' val=1.23 tag='exist'>, <Val:type='num' val=12 tag='int'>, <Val:type='num' val=123 tag='a_number'>, <Val:type='str' val=FUN tag='_str'>, <Val:type='num' val=2 tag='b'>, <Val:type='num' val=1.23 tag='exist'>]
