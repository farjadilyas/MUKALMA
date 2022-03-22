# Library for extracting Subject - Verb/Adjective - Object Triples 
# from a Raw Text input using Spacy and NLTK
# -- Utility Functions -- 

# Nabeel Danish

# Imports
import en_core_web_sm
from collections.abc import Iterable

# Defining NLP 
nlp = en_core_web_sm.load()

# Dependency Markers for tokens that are used to identify them in the 
# parser tree formed by the nltk POS Tagging
SUBJECTS = {"nsubj", "nsubjpass", "csubj", "csubjpass", "agent", "expl"}
OBJECTS = {"dobj", "dative", "attr", "oprd"}
BREAKER_POS = {"CCONJ", "VERB"}
NEGATIONS = {"no", "not", "n't", "never", "none"}
ADJECTIVES = {"acomp", "advcl", "advmod", "amod", "appos", "nn", "nmod", "ccomp", "complm",
              "hmod", "infmod", "xcomp", "rcmod", "poss"," possessive"}
COMPOUNDS = {"compound"}
PREPOSITIONS = {"prep"}

# Keywords used for entity mappings
conjunctions = {"and", "or", "yet", "nor", "but", "so", "for"}

# Keywords used for POS Tagging matching
NOUN = "NOUN"
VERB = "VERB"
AUX = "AUX"
SUB = "SUB"
ADP = "ADP"
PRON = "PRON"
DET = "DET"
CCONJ = "CCONJ"

me = "me"
pobj = "pobj"
prep = "prep"
agent = "agent"
xcomp = "xcomp"
aux = "aux"
auxpass = "auxpass"
that = "that"
lefts = 'lefts'
rights = 'rights'

# Used to escape characters
escapes = ''.join([chr(char) for char in range(1, 32)])
translator = str.maketrans('', '', escapes)

# Function to generate and clean SVOs
def cleanGenerateSVAOs(s, va, o):
    s = s.translate(translator)
    va = va.translate(translator)
    o = o.translate(translator)
    return (s, va, o)

# Function to check for a conjunction in the tokens
def containsConjunction(depSet):
    for conjunction in conjunctions:
        if conjunction in depSet:
            return True
    return False 
# End of function

# Function to check for a negated Verb
def isNegated(tok):
    parts = list(tok.lefts) + list(tok.rights)
    for dep in parts:
        if dep.lower_ in NEGATIONS:
            return True
    return False
# End of function

# Function to retrieve the entities (subjects/objects) around a particular entity that are linked
# using Conjunctions
def getEntitiesFromConjunctions(entities, subject=True):
    moreEntities = []
    for entity in entities:
        rightEntities = list(entity.rights)
        rightDeps = { tok.lower_ for tok in rightEntities }

        if containsConjunction(rightDeps):
            # Switch Case for subject/objects
            if subject:
                moreEntities.extend([tok for tok in rightEntities if tok.dep_ in SUBJECTS or tok.pos_ == NOUN])
            else:
                moreEntities.extend([tok for tok in rightEntities if tok.dep_ in OBJECTS or tok.pos_ == NOUN])
            
            # Recursion check to see if we found an entity so we keep continuing that direction
            if len(moreEntities) > 0:
                moreEntities.extend(getEntitiesFromConjunctions(moreEntities, subject))
    # End for
    return moreEntities
# End of function

# Function to traverse the parsed tree and find subjects
def findSubjects(token):
    head = token.head

    # Iterating to reach either a verb or a noun
    while head.pos_ != VERB and head.pos_ != NOUN and head.head != head:
        head = head.head
    
    # If we stop at a VERB
    if head.pos_ is VERB:
        subjects = [tok for tok in head.lefts if tok.dep_ == SUB]
        
        if len(subjects) > 0:
            negatedVerb = isNegated(head)
            subjects.extend(getEntitiesFromConjunctions(subjects))
            return subjects, negatedVerb
        elif head.head != head:
            return findSubjects(head)

    elif head.pos_ == NOUN:
        return [head], isNegated(token)

    return [], False
# End of function

# Function to get Objects that are linked using prepositions
def getObjectsFromPrepositions(deps, passive):
    objects = []
    for dep in deps:
        if dep.pos_ == ADP and (dep.dep_ == prep or (passive and dep.dep_ == agent)):
            objects.extend([tok for tok in dep.rights if tok.dep_ in OBJECTS or 
                            (tok.pos_ == PRON and tok.lower_ == me) or
                            (passive and tok.dep_ == pobj)])
        # End if
    # End for
    return objects
# End of function

# Function to get objects from open complements - xcomp, where verb has no subject
def getObjectsFromXCOMP(deps, passive):
    for dep in deps:
        if dep.pos_ == VERB and dep.dep_ == xcomp:
            verb = dep
            rightObjects = list(verb.rights)
            objects = [tok for tok in rightObjects if tok.dep_ in OBJECTS]
            objects.extend(getObjectsFromPrepositions(rightObjects, passive))
            if len(objects) > 0:
                return verb, objects 
            # End if
        # End if
    # End for
    return None, None
# End of function

# Function to get all the objects that are linked with Adjectives
def getAllObjectsWithAdjectives(verb, passive):
    rightObjects = list(verb.rights)
    objects = [tok for tok in rightObjects if tok.dep_ in OBJECTS]

    if len(objects) == 0:
        objects = [tok for tok in rightObjects if tok.dep_ in ADJECTIVES]

    # Getting Objects from Adjectives
    objects.extend(getObjectsFromPrepositions(rightObjects, passive))

    # Getting Objects from XCOMP
    potentialNewVerb, potentialNewObjects = getObjectsFromXCOMP(rightObjects, passive)
    if potentialNewVerb is not None and potentialNewObjects is not None and len(potentialNewObjects) > 0:
        objects.extend(potentialNewObjects)
        verb = potentialNewVerb
    if len(objects) > 0:
        objects.extend(getEntitiesFromConjunctions(objects, subject=False))
    
    return verb, objects
# End of function

# Function to generate Adjectives on the Left and Right side of the 
# Given Object
def generateLeftRightAdjectives(object):
    objectDescTokens = []
    
    # Traversing the Left tree
    for tok in object.lefts:
        if tok.dep_ in ADJECTIVES:
            objectDescTokens.extend(generateLeftRightAdjectives(tok))
        # End if
    # End for
    objectDescTokens.append(object)

    # Traversing the Right Tree
    for tok in object.rights:
        if tok.dep_ in ADJECTIVES:
            objectDescTokens.extend(generateLeftRightAdjectives(tok))
        # End if
    # End for

    return objectDescTokens
# End of function

# Function to generate Sub Compound from the given subject
def generateSubCompound(subject):
    subCompound = []
    
    # Traversing the left sub-tree
    for tok in subject.lefts:
        if tok.dep_ in COMPOUNDS:
            subCompound.extend(generateSubCompound(tok))
        # End if
    # End for

    subCompound.append(subject)

    # Traversing the right sub-tree
    for tok in subject.rights:
        if tok.dep_ in COMPOUNDS:
            subCompound.extend(generateSubCompound(tok))
        # End if
    # End for

    return subCompound
# End of function

# Function to get all the subjects adjacent to the verb passed to it
def getAllSubjects(verb):
    verbNegated = isNegated(verb)
    subjects = [tok for tok in verb.lefts if tok.dep_ in SUBJECTS and tok.pos_ != DET]
    
    if len(subjects) > 0:
        subjects.extend(getEntitiesFromConjunctions(subjects))
    else:
        foundSubjects, verbNegated = findSubjects(verb)
        subjects.extend(foundSubjects)

    return subjects, verbNegated
# End of function

# Function to check if the given token is a non auxiliary verbs
def isNonAuxVerb(token):
    return token.pos_ == VERB and (token.dep_ != aux and token.dep_ != auxpass)
# End of function

# Function to check if the given token is a verb (aux or not)
def isVerb(token):
    return token.pos_ == VERB or token.pos_ == AUX
# End of function

# Function to find all the verbs
def findVerbs(tokens):
    verbs = [tok for tok in tokens if isNonAuxVerb(tok)]
    
    # If we cannot find all the main verbs, auxiliary verbs
    if len(verbs) == 0:
        verbs = [tok for tok in tokens if isVerb(tok)]
    
    return verbs
# End of function

# Function to return the verb to the right of given verb linked in a 
# conjunction relation, if applicable
def rightOfVerbIsConjuctiveVerb(verb):
    rightVerbs = list(verb.rights)

    # Check for the pattern VERB -> CONJUCTION -> VERB
    if len(rightVerbs) > 1 and rightVerbs[0].pos_ == CCONJ:
        for tok in rightVerbs[1:]:
            if isNonAuxVerb(tok):
                return True, tok 
            # End if
        # End for
    # End if

    return False, verb
# End of function

# Function to get all the objects for an active/passive sentence
def getAllObjects(verb, passive):
    rightObjects = list(verb.rights)

    objects = [tok for tok in rightObjects if tok.dep_ in OBJECTS or (passive and tok.dep_ == pobj)]
    objects.extend(getObjectsFromPrepositions(rightObjects, passive))

    # Potential verbs without subjects
    potentialNewVerb, potentialNewObjects = getObjectsFromXCOMP(rightObjects, passive)

    # Extending
    if potentialNewVerb is not None and potentialNewObjects is not None and len(potentialNewObjects) > 0:
        objects.extend(potentialNewObjects)
        verb = potentialNewVerb 
    if len(objects) > 0:
        objects.extend(getEntitiesFromConjunctions(objects, subject=False))
    
    return verb, objects
# End of function

# Function to check for passive sentences
def isPassive(tokens):
    for tok in tokens:
        if tok.dep_ == auxpass:
            return True 
        # End if
    # End for
    return False 
# End of function

# Function to resolve SUBJECT 'that' OBJECT if found
def getTHATResolution(tokens):
    for tok in tokens:
        if that in [t.orth_ for t in tok.lefts]:
            return tok.head 
        # End if
    # End for
    return None 
# End of function

# Expanding the object / subject NP using a small chunk of the
# tree
def expand(item, tokens, visited):
    if item.lower_ == that:
        tempItem = getTHATResolution(tokens)
        if tempItem is not None:
            item = tempItem
    
    parts = []

    # If the item has lefts
    if hasattr(item, lefts):
        for part in item.lefts:
            if part.pos_ in BREAKER_POS:
                break 
            if not part.lower_ in NEGATIONS:
                parts.append(part)
        # End for
    # End if
    parts.append(item)

    # If the item has rights
    if hasattr(item, rights):
        for part in item.rights:
            if part.pos_ in BREAKER_POS:
                break
            if not part.lower_ in NEGATIONS:
                parts.append(part)
        # End for
    # End if

    if hasattr(parts[-1], rights):
        for item2 in parts[-1].rights:
            if item2.pos_ == DET or item2.pos_ == NOUN:
                if item2.i not in visited:
                    visited.add(item2.i)
                    parts.extend(expand(item2, tokens, visited))
                # End if
            # End if
            break 
        # End for
    # End if

    return parts 
# End of function

# Function to convert the NLTK token object into a string
def toString(tokens):
    if isinstance(tokens, Iterable):
        return ' '.join([item.text for item in tokens])
    else:
        return ''
# End of function
