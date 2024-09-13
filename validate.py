from openai import OpenAI   
import urllib
import dotenv
import os
from rdflib import Namespace, Graph

dotenv.load_dotenv(".env", override=True)

client = OpenAI(
  api_key = os.environ.get("OPENAI_KEY"),
  organization = os.environ.get("OPENAI_ORGANIZATION") 
)
  
''' 
@returns Assistant ID
''' 
def createAssistant():
  assistant = client.beta.assistants.create(
    name="Gemeentelijke ambtenaar",
    instructions="U bent een gemeentelijke ambtenaar in Vlaanderen. U verwijst naar de artikelen van wetgeving of delen van documenten die zijn gebruikt bij het nemen van een beslissing.",
    model="gpt-4o", 
    tools=[{"type": "file_search"}]
  )
  return assistant

def createVectorStore():
  #Create a vector store 
  vector_store = client.beta.vector_stores.create(name="Gemeentelijke besluiten")
  return vector_store


def uploadFiles (url, vector_store):
  

    
  file_streams = [open("download.pdf", "r")]
  
  # Use the upload and poll SDK helper to upload the files, add them to the vector store,
  # and poll the status of the file batch for completion.
  file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
    vector_store_id=vector_store.id, files=file_streams
  )
  
  # You can print the status and the file counts of the batch to see the result of this operation.
  print(file_batch.status)
  print(file_batch.file_counts)

'''TODO: load the data about the application (aanvraag) from the triple store (based on the ID)
'''
def validate( besluit_id, aanvraag_text):
  erf = Namespace('https://id.erfgoed.net/vocab/ontology#')
  RDF = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
  DCT = Namespace('http://purl.org/dc/terms/')

  g = Graph()
  uri = "https://id.erfgoed.net/besluiten/{}".format(besluit_id)
  print (uri)
  g.parse(uri)

  for s, p, o in g.triples((None, RDF.type, erf.Attachment)):
      dctype = g.value(s, DCT.type)
      if (str(g.value(dctype, DCT.title)) == 'Besluit'):
          attachment_id = g.value(dctype, DCT.title)
          print("The PDF for besluit ID {} can be found at {}".format(besluit_id, s))
          besluit_pdf = s
                
  #Download file if not exist
  if not os.path.isfile("download.pdf"):
      urllib.request.urlretrieve(besluit_pdf, "download.pdf")
  
  # Ready the files for upload to OpenAI
  
  assistant = createAssistant()
  
  vector_store = createVectorStore()
  
  #uploadFiles(["download.pdf"], vector_store)

  assistant = client.beta.assistants.update(
    assistant_id=assistant.id,
    tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
  )

  # Upload the user provided file to OpenAI
  message_file = client.files.create(
    file=open("download.pdf", "rb"), purpose="assistants"
  )
  
  # Create a thread and attach the file to the message
  thread = client.beta.threads.create(
    messages=[
      {
        "role": "user",
        "content": "{} Is er een vergunning nodig voor deze handeling volgens deze besluit en waarom?".format(aanvraag_text),
        # Attach the new file to the message.
        "attachments": [
          { "file_id": message_file.id
          , "tools": [{"type": "file_search"}]
          }
        ],
      }
    ]
  )
  # The thread now has a vector store with that file in its tool resources.
  print(thread.tool_resources.file_search)

  # Use the create and poll SDK helper to create a run and poll the status of
  # the run until it's in a terminal state.

  run = client.beta.threads.runs.create_and_poll(
      thread_id=thread.id, assistant_id=assistant.id
  )

  messages = list(client.beta.threads.messages.list(thread_id=thread.id, run_id=run.id))

  message_content = messages[0].content[0].text
  annotations = message_content.annotations
  citations = []
  for index, annotation in enumerate(annotations):
      message_content.value = message_content.value.replace(annotation.text, f"[{index}]")
      if file_citation := getattr(annotation, "file_citation", None):
          cited_file = client.files.retrieve(file_citation.file_id)
          citations.append(f"[{index}] {cited_file.filename}")

  print(message_content.value)
  print("\n".join(citations))

if __name__ == '__main__':

  validate(14850,  "Ik ben van plan om een trap te plaatsen.")







