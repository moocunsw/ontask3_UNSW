import React from "react";
import { Modal, Button, Icon } from "antd";

class PreviewModal extends React.Component {
  constructor(props) {
    super(props);

    this.state = { index: 0 };
  }

  handleClose = () => {
    const { onClose } = this.props;

    this.setState({ index: 0 });
    onClose();
  };

  render() {
    const { preview } = this.props;
    const { index } = this.state;
    const { populatedContent, data, visible } = preview;
    
    return (
      <Modal
        visible={visible}
        title={`Preview content: ${index + 1}`}
        onCancel={this.handleClose}
        footer={null}
      >
        <div style={{ display: "flex", flexDirection: "column" }}>
          <Button.Group
            size="large"
            style={{ marginBottom: "10px", textAlign: "center" }}
          >
            <Button
              type="primary"
              disabled={index === 0 || populatedContent.length === 0}
              onClick={() => this.setState({ index: index - 1 })}
            >
              <Icon type="left" />Previous
            </Button>

            <Button
              type="primary"
              disabled={
                index === populatedContent.length - 1 ||
                populatedContent.length === 0
              }
              onClick={() => this.setState({ index: index + 1 })}
            >
              Next<Icon type="right" />
            </Button>
          </Button.Group>

          {populatedContent.length > 0 ? (
            <div
              style={{ padding: "10px", border: "1px solid #F1F1F1" }}
              dangerouslySetInnerHTML={{
                __html: populatedContent[index]
              }}
            />
          ) : (
            <div
              style={{
                padding: "10px",
                border: "1px solid #F1F1F1",
                textAlign: "center"
              }}
            >
              After filtering, no results were returned from your view.
            </div>
          )}
        </div>
      </Modal>
    );
  }
}

export default PreviewModal;