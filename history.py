import wikipediaapi
import random

def get_wiki_history(year):
        year = str(year)
        wiki_wiki = wikipediaapi.Wikipedia('en')

        page_py = wiki_wiki.page(year)
        for s in page_py.sections:
                if s.title == 'Events':
                        my_section = s
                        if( len(s.sections) > 0 ):
                                my_section = random.choice(s.sections)
                        events = my_section.text.split('\n')
                        i = random.randrange(0,len(events))
                        while(not events[i].lower().startswith( ('jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'))):
                                i = random.randrange(0,len(events))
                        
                        result = events[i]

                        if( len(events[i]) < 15 ):
                                result = result + ' ' + events[i+1]
                        elif( ):
                                result = result[i-1] + ' ' + result

                        return year + ' - ' + result
        return "Nothin happened in " + year