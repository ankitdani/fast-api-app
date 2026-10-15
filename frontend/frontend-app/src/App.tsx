import { useEffect, useState } from "react";
import api from "./api";

type item = {
  id: number;
  name: string;
  description: string;
};

function App() {
  const [items, setItems] = useState<item[]>([]);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [id, setId] = useState<number>(0);
  const [selectedItem, setSelectedItem] = useState<item>();
  const [selectAllItems, setSelectAllItems] = useState<boolean>(false);
  const [deleteId, setDeleteId] = useState<number>(0);
  const [updateId, setUpdateId] = useState<number>(0);
  const [updateDescription, setUpdateDescription] = useState<string>("");
  const [token, setToken] = useState<string | null>(
    localStorage.getItem("token"),
  );
  const [username, setUsername] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [summary, setSummary] = useState<string>("");
  const [chatMessage, setChatMessage] = useState("");
  const [chatReply, setChatReply] = useState("");
  const [pendingDelete, setPendingDelete] = useState<{
    item_id: number;
    item_name: string;
  } | null>(null);

  useEffect(() => {
    fetchItems();
    // fetchItem(id);
  }, []);

  const handleRegister = async () => {
    try {
      await api.post(`/users/register`, {
        username,
        password,
      });
      const accessToken = await login(username, password);
      localStorage.setItem("token", accessToken);
      setToken(accessToken);
    } catch (error) {
      console.log(error);
    }
  };

  const handleLogin = async () => {
    try {
      const accessToken = await login(username, password);
      localStorage.setItem("token", accessToken);
      setToken(accessToken);
    } catch (error) {
      console.log(error);
    }
  };

  const fetchItems = async () => {
    try {
      const response = await api.get(`/items/`);
      setItems(response.data);
    } catch (error) {
      console.log(error);
    }
  };

  const fetchItem = async (item_id: number) => {
    try {
      const response = await api.get(`/items/${item_id}`);
      setSelectedItem(response.data);
    } catch (error) {
      console.log(error);
    }
  };

  const createItem = async () => {
    try {
      const response = await api.post(`/items/`, {
        name: name,
        description: description,
      });
      setItems([...items, response.data]);
      setName("");
      setDescription("");
    } catch (error) {
      console.log(error);
    }
  };

  const deleteItem = async (item_id: number) => {
    try {
      await api.delete(`/items/${item_id}`);
      await fetchItems();
      if (selectedItem?.id === item_id) {
        setSelectedItem(undefined);
      }
    } catch (error) {
      console.log(error);
    }
  };

  const updateItem = async (item_id: number) => {
    try {
      await api.put(`/items/${item_id}`, {
        name,
        description: updateDescription,
      });
      await fetchItems();
      setUpdateId(0);
      setUpdateDescription("");
    } catch (error) {
      console.log(error);
    }
  };

  const login = async (username: string, password: string) => {
    const params = new URLSearchParams(); // create data in URL-encoded form format
    params.append("username", username);
    params.append("password", password);
    const response = await api.post(`/users/login`, params);
    return response.data.access_token;
  };

  const fetchSummary = async () => {
    try {
      const response = await api.get(`/items/summary/`);
      setSummary(response.data.summary);
    } catch (error) {
      console.log(error);
    }
  };

  const sendChat = async () => {
    try {
      const response = await api.post(`/items/chat`, { message: chatMessage });
      if (response.data.requires_confirmation) {
        setChatReply(response.data.message);
        setPendingDelete({
          item_id: response.data.item_id,
          item_name: response.data.item_name,
        });
      } else {
        setChatReply(response.data.reply);
        setPendingDelete(null);
      }
      setChatMessage("");
    } catch (error) {
      console.log(error);
    }
  };

  const confirmDelete = async () => {
    if (!pendingDelete) {
      return;
    }
    await deleteItem(pendingDelete.item_id);
    setChatReply(`Deleted ${pendingDelete.item_name}.`);
    setPendingDelete(null);
  };

  return (
    <div className="min-h-screen p-8 bg-gray-200 mx-auto space-y-3 max-w-2xl">
      <div className="bg-white rounded shadow p-2 flex flex-wrap gap-3 items-center">
        <input
          className="border rounded shadow p-2 flex-1 min-w-[120px]"
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          className="border rounded shadow p-2 flex-1 min-w-[120px]"
          type="text"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button
          className="bg-blue-700 text-white px-4 py-2 rounded"
          onClick={handleRegister}
        >
          Register
        </button>
        {token && <span>Sign Up Successful!</span>}
        <button
          className="bg-blue-700 text-white px-4 py-2 rounded"
          onClick={handleLogin}
        >
          Login
        </button>
        {token && <span>Logged In</span>}
      </div>
      <div className="bg-white rounded p-2 shadow flex flex-wrap gap-3 items-center min-w-[120px]">
        <input
          className="border rounded p-2"
          type="text"
          placeholder="Username"
          value={name}
          onChange={(e) => {
            setName(e.target.value);
          }}
        />
        <input
          className="border rounded p-2"
          type="text"
          placeholder="Password"
          value={description}
          onChange={(e) => {
            setDescription(e.target.value);
          }}
        />
        <button
          className="g-blue-700 text-white px-4 py-2 rounded"
          onClick={createItem}
        >
          Create
        </button>
      </div>
      <div className="bg-white rounded p-2 shadow flex flex-wrap gap-3 items-center min-w-[120px]">
        <input
          className="border rounded p-2"
          type="number"
          value={id}
          onChange={(e) => {
            setId(Number(e.target.value));
          }}
        />
        <button
          className="bg-blue-700 text-white px-4 py-2 rounded"
          onClick={() => {
            fetchItem(id);
          }}
        >
          Get 1 item
        </button>
        {selectedItem && (
          <div>
            {selectedItem.name} {selectedItem.description}
          </div>
        )}
      </div>

      <div className="bg-white rounded p-2 shadow flex flex-wrap gap-3 items-center min-w-[120px]">
        <button
          className="bg-blue-700 text-white px-4 py-2 rounded"
          onClick={() => {
            fetchItems();
            setSelectAllItems(true);
          }}
        >
          Get All
        </button>
        <button
          className="bg-blue-700 text-white px-4 py-2 rounded"
          onClick={() => setSelectAllItems(false)}
        >
          Clear
        </button>
        {selectAllItems &&
          items.map((item) => (
            <div key={item.id}>
              #{item.id} - {item.description}
            </div>
          ))}
      </div>

      <div className="bg-white rounded p-2 shadow flex flex-wrap gap-3 items-center min-w-[120px]">
        <input
          className="border rounded p-2"
          type="number"
          value={deleteId}
          onChange={(e) => {
            setDeleteId(Number(e.target.value));
          }}
        ></input>
        <button
          className="bg-blue-700 text-white px-4 py-2 rounded"
          onClick={() => {
            deleteItem(deleteId);
          }}
        >
          Delete
        </button>
      </div>
      <div className="bg-white rounded p-2 shadow flex flex-wrap gap-3 items-center min-w-[120px]">
        <button
          className="bg-blue-700 text-white px-4 py-2 rounded"
          onClick={() => updateItem(updateId)}
        >
          Update
        </button>
        <input
          className="border rounded px-3 py-2 w-24"
          placeholder="Add ID to update"
          type="number"
          value={updateId}
          onChange={(e) => setUpdateId(Number(e.target.value))}
        ></input>
        <input
          className="border rounded p-2"
          placeholder="New item description"
          value={updateDescription}
          onChange={(e) => setUpdateDescription(e.target.value)}
        ></input>
      </div>
      <div className="bg-white rounded p-2 shadow flex min-w-[120px]">
        <button
          className="bg-blue-700 text-white px-4 py-2 rounded"
          onClick={fetchSummary}
        >
          Get Summary
        </button>
        {summary && <div>{summary}</div>}
      </div>
      <div className="bg-white rounded p-2 shadow flex flex-wrap gap-3 items-center min-w-[120px]">
        <input
          className="border rounded p-2"
          placeholder="Ask something..."
          value={chatMessage}
          type="text"
          onChange={(e) => setChatMessage(e.target.value)}
        />
        <button
          className="bg-blue-700 text-white px-4 py-2 rounded"
          onClick={sendChat}
        >
          Send Chat
        </button>
        {chatReply && <div>{chatReply}</div>}
        {pendingDelete && (
          <button
            className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
            onClick={confirmDelete}
          >
            Confirm Delete `{pendingDelete.item_name}`
          </button>
        )}
      </div>
    </div>
  );
}

export default App;
