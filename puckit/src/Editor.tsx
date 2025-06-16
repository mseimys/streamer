import { FieldLabel, Puck, usePuck, type Config } from "@measured/puck";
import "@measured/puck/puck.css";
import html2canvas from "html2canvas";

const ImageUploadField = ({ value, onChange, name }) => {
  const handleUpload = async (event) => {
    const file = event.target.files;
    if (!file) return;

    const url = URL.createObjectURL(file[0]); // For demo purposes, using local URL
    onChange(url);
  };

  return (
    <div>
      {value && <img src={value} width="100" alt="logo preview" />}
      <input type="file" accept="image/*" onChange={handleUpload} />
    </div>
  );
};

// Create Puck component config
const config: Config = {
  root: {
    fields: {
      fontFamily: {
        type: "select",
        label: "Font",
        options: [
          { value: "Arial", label: "Arial" },
          { value: "Courier New", label: "Courier New" },
          { value: "Georgia", label: "Georgia" },
          { value: "Times New Roman", label: "Times New Roman" },
        ],
      },
      //... other root fields
    },
  },
  components: {
    HeadingBlock: {
      fields: {
        children: {
          type: "text",
          label: "Heading Text",
          placeholder: "Enter heading text",
        },
      },
      render: ({ children, fontFamily }) => {
        return (
          <div style={{ fontWeight: 500, fontSize: "40px", fontFamily }}>
            {children || "Enter heading text"}
          </div>
        );
      },
    },
    TitleBlock: {
      fields: {
        text: { type: "text" },
        color: { type: "text" }, // Could be a custom color picker field
        fontSize: { type: "number", min: 8, max: 128 },
      },
      render: ({ color, fontSize, text }) => (
        <h1 style={{ color, fontSize: `${fontSize}px` }}>{text}</h1>
      ),
    },
    Image: {
      fields: {
        logoUrl: {
          type: "custom",
          label: "Company Logo",
          render: ({ value, onChange, name, field }) => (
            <FieldLabel label={field.label || ""}>
              <ImageUploadField value={value} onChange={onChange} name={name} />
            </FieldLabel>
          ),
        },
        //... other fields like size, alignment etc.
      },
      render: ({ logoUrl }) => {
        if (!logoUrl) return <div>Upload a logo</div>;
        return (
          <img src={logoUrl} alt="Company Logo" style={{ maxWidth: "100%" }} />
        );
      },
    },
  },
};

// Describe the initial data
const initialData = {
  content: [
    {
      props: { children: "Hello!", id: "id" },
      type: "HeadingBlock",
    },
  ],
  root: {},
};

// Save the data to your database
const save = (data) => {
  console.log("Saving data:", data);
  // make a screenshot of the preview window identified by id="puck-preview"
  // const previewElement = document.getElementById("puck-canvas-root");
  const iframe: HTMLIFrameElement = document.getElementById("preview-frame");
  const previewElement = iframe?.contentWindow?.document.body;
  if (previewElement) {
    console.log("Taking screenshot of preview element", previewElement);
    html2canvas(previewElement).then((canvas) => {
      canvas.toBlob((blob) => {
        if (!blob) {
          console.error("Failed to create blob from canvas");
          return;
        }
        // const imageData = canvas.toDataURL("image/png");
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "screenshot.png";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      });
    });
  }
};

// Render Puck editor
export function Editor() {
  return (
    <Puck
      config={config}
      data={initialData}
      onPublish={save}
      viewports={[
        {
          width: 1080,
          height: 1080,
          icon: "1:1", // Tablet
        },
        {
          width: 400,
          height: 500,
          icon: "4:5",
        },
        {
          width: 1600,
          height: 900,
          icon: "16:9",
        },
      ]}
      overrides={{
        headerActions: ({ children }) => {
          const appState = usePuck((s) => s.appState);

          return (
            <>
              <button
                type="button"
                style={{
                  border: "none",
                  color: "var(--puck-color-grey-12)",
                  backgroundColor: "var(--puck-color-azure-04)",
                  padding: "10px 20px",
                  borderRadius: "5px",
                }}
                onClick={() => {
                  save(appState.data);
                }}
              >
                Save Template
              </button>

              {/* Render default header actions, such as the default Button */}
              {/*{children}*/}
            </>
          );
        },
      }}
    />
  );
}
