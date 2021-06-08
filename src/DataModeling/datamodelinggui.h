#ifndef DATAMODELINGGUI_H
#define DATAMODELINGGUI_H

#include <QMainWindow>

namespace Ui {
class DataModelingGUI;
}

class DataModelingGUI : public QMainWindow
{
    Q_OBJECT

public:
    explicit DataModelingGUI(QWidget *parent = 0);
    ~DataModelingGUI();

private:
    Ui::DataModelingGUI *ui;
};

#endif // DATAMODELINGGUI_H
