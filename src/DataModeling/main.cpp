#include "datamodelinggui.h"
#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    DataModelingGUI w;
    w.show();

    return a.exec();
}
