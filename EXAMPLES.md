# Usage Examples - IFS Customization Agent Studio

This document shows realistic examples of how the IFS Customization Agent Studio works.

## Example 1: Creating a Custom Field

### User Query:
```
How do I create a custom field in IFS Cloud?
```

### Agent Response:
```
To create a custom field in IFS Cloud, you'll need to work with projections and 
client configurations. Here's a complete example:

1. **Define the custom field in your projection:**

```sql
projection MyCustomProjection {
    entity CustomerInfo {
        -- Add your custom field
        attribute CustomField Text {
            label = "Custom Field";
            maxlength = 100;
        }
        
        -- Enable the field for database
        crud = Create Read Update Delete;
    }
}
```

2. **Add the field to your client page:**

```javascript
fragment CustomerInfoFragment {
    field CustomField {
        label = "My Custom Field";
        required = [true];
        editable = [true];
    }
}
```

3. **Implement any business logic (optional):**

```plsql
PROCEDURE Validate_Custom_Field (
   attr_ IN OUT VARCHAR2 )
IS
   custom_field_ VARCHAR2(100);
BEGIN
   custom_field_ := Client_SYS.Get_Item_Value('CUSTOM_FIELD', attr_);
   
   -- Add your validation logic
   IF custom_field_ IS NULL THEN
      Error_SYS.Record_General(lu_name_, 'CUSTOMFIELDEMPTY: Custom field cannot be empty');
   END IF;
END Validate_Custom_Field;
```

This approach follows IFS Cloud best practices for extending standard functionality 
with custom fields.
```

---

## Example 2: Adding a Custom Button

### User Query:
```
Show me code to add a custom button to an IFS page
```

### Agent Response:
```
Here's how to add a custom button (command) to an IFS Cloud page:

1. **Define the command in your client file:**

```javascript
client MyCustomClient;

page CustomerInfo {
    selector {
        field CustomerNo;
        field Name;
    }
    
    // Add your custom command
    command MyCustomCommand {
        label = "Process Customer";
        mode = SelectedRecords;
        enabled = [true];
        execute {
            call ProcessCustomer(CustomerNo);
            success("Customer processed successfully!");
            refresh();
        }
    }
}
```

2. **Implement the backend function in your projection:**

```sql
function ProcessCustomer(
    customer_no_ Text
) return Text {
    implementation = "MyCustomImplementation";
}
```

3. **Create the PL/SQL implementation:**

```plsql
FUNCTION Process_Customer (
   customer_no_ IN VARCHAR2 
) RETURN VARCHAR2
IS
   result_ VARCHAR2(2000);
BEGIN
   -- Your business logic here
   result_ := 'Customer ' || customer_no_ || ' processed';
   
   -- Commit the changes
   COMMIT;
   
   RETURN result_;
END Process_Customer;
```

The button will appear in the page toolbar and can execute when records are selected.
```

---

## Example 3: Custom Event Action

### User Query:
```
How do I implement a custom event action in IFS?
```

### Agent Response:
```
To implement a custom event action in IFS Cloud, you can use event handlers in your 
projection. Here's a complete example:

**1. Define the event in your projection:**

```sql
projection CustomerProjection {
    entity Customer {
        attribute CustomerNo Text;
        attribute Name Text;
        
        // Define custom event
        event CustomerUpdated {
            parameter CustomerNo Text;
            parameter OldName Text;
            parameter NewName Text;
        }
    }
}
```

**2. Trigger the event in your PL/SQL code:**

```plsql
PROCEDURE Update_Customer (
   customer_no_ IN VARCHAR2,
   new_name_    IN VARCHAR2
)
IS
   old_name_ VARCHAR2(200);
BEGIN
   old_name_ := Get_Name(customer_no_);
   
   -- Update the customer
   UPDATE customer_tab
   SET name = new_name_
   WHERE customer_no = customer_no_;
   
   -- Raise the custom event
   Raise_Customer_Updated_Event___(
      customer_no_ => customer_no_,
      old_name_    => old_name_,
      new_name_    => new_name_
   );
   
   COMMIT;
END Update_Customer;
```

**3. Subscribe to the event in your client:**

```javascript
client CustomerClient;

page CustomerPage {
    subscribe CustomerUpdated {
        when [CustomerNo = "${pageContext.CustomerNo}"] {
            info("Customer ${NewName} was updated from ${OldName}");
            refresh();
        }
    }
}
```

This pattern allows you to create reactive behavior in your IFS Cloud applications.
```

---

## Example 4: API Integration

### User Query:
```
What's the best way to integrate with IFS API?
```

### Agent Response:
```
Here's a comprehensive example of integrating with IFS Cloud APIs:

**1. Using the REST API from external applications:**

```python
import requests
import json

class IFSAPIClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def get_customer(self, customer_no):
        """Get customer information"""
        url = f"{self.base_url}/main/ifsapplications/projection/v1/CustomerInfo.svc/Customers('{customer_no}')"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def create_customer(self, customer_data):
        """Create a new customer"""
        url = f"{self.base_url}/main/ifsapplications/projection/v1/CustomerInfo.svc/Customers"
        response = self.session.post(url, json=customer_data)
        response.raise_for_status()
        return response.json()
    
    def update_customer(self, customer_no, updates, etag):
        """Update customer information"""
        url = f"{self.base_url}/main/ifsapplications/projection/v1/CustomerInfo.svc/Customers('{customer_no}')"
        headers = {'If-Match': etag}
        response = self.session.patch(url, json=updates, headers=headers)
        response.raise_for_status()
        return response.json()

# Usage example
client = IFSAPIClient(
    base_url='https://your-ifs-instance.com',
    username='your_username',
    password='your_password'
)

# Get customer
customer = client.get_customer('CUST001')
print(f"Customer: {customer['Name']}")

# Create customer
new_customer = {
    'CustomerNo': 'CUST002',
    'Name': 'New Customer Inc.',
    'Country': 'US'
}
result = client.create_customer(new_customer)
```

**2. Using OAuth 2.0 authentication (recommended for production):**

```python
from requests_oauthlib import OAuth2Session

def get_ifs_oauth_client(client_id, client_secret, token_url, base_url):
    """Get OAuth2 authenticated IFS client"""
    client = OAuth2Session(client_id)
    token = client.fetch_token(
        token_url=token_url,
        client_id=client_id,
        client_secret=client_secret
    )
    
    return client

# Usage
oauth_client = get_ifs_oauth_client(
    client_id='your_client_id',
    client_secret='your_client_secret',
    token_url='https://your-ifs-instance.com/auth/realms/your-realm/protocol/openid-connect/token',
    base_url='https://your-ifs-instance.com'
)

# Make API calls
response = oauth_client.get(
    'https://your-ifs-instance.com/main/ifsapplications/projection/v1/CustomerInfo.svc/Customers'
)
```

These patterns provide secure and efficient ways to integrate with IFS Cloud APIs.
```

---

## Interactive Session Example

```
$ python main.py

======================================================================
🤖 IFS Customization Agent Studio - Interactive Mode
======================================================================

Ask questions about IFS customization and get code examples!
Commands:
  - Type your question to get an answer
  - 'clear' - Clear conversation history
  - 'stats' - Show database statistics
  - 'quit' or 'exit' - Exit the application
======================================================================

You: How do I add validation to a field?

🤔 Thinking...

Agent: To add validation to a field in IFS Cloud, you can use several approaches:

1. **Client-side validation:**
   [Provides code example]

2. **Server-side validation:**
   [Provides code example]

3. **Custom validation functions:**
   [Provides code example]

----------------------------------------------------------------------

You: stats

📊 Database Statistics:
   Total chunks: 1247
   Collection: ifs_documentation

You: clear

✅ Conversation history cleared.

You: quit

👋 Goodbye!
```

---

## Tips for Best Results

1. **Be specific in your queries**: Instead of "How do I customize IFS?", ask "How do I add a custom field to the Customer page?"

2. **Ask for code examples**: The system is optimized for providing code, so include phrases like "show me code" or "provide an example"

3. **Follow-up questions**: The system maintains conversation history, so you can ask follow-up questions

4. **Use the stats command**: Check how much documentation is indexed to understand coverage

5. **Rebuild database periodically**: Re-scrape documentation to get the latest updates

---

## Command Line Examples

```bash
# Scrape 100 pages of documentation
python main.py --scrape --max-pages 100

# Ask a single question
python main.py --query "How do I create a custom projection?"

# Use a custom database location
python main.py --db-path /path/to/my/database

# Scrape from a specific URL
python main.py --scrape --url https://docs.ifs.com/techdocs/cloud/
```
