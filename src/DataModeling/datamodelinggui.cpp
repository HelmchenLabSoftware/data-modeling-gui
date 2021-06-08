#include "datamodelinggui.h"
#include "ui_datamodelinggui.h"

DataModelingGUI::DataModelingGUI(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::DataModelingGUI)
{
    ui->setupUi(this);
}

DataModelingGUI::~DataModelingGUI()
{
    delete ui;
}
