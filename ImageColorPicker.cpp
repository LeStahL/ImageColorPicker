/* Image Color Picker by Team210
 * Copyright (C) 2019  Alexander Kraus <nr4@z10.info>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

#include "ImageColorPicker.hpp"
#include "ui_ImageColorPicker.h"

#include <QMimeData>
#include <QGraphicsPixmapItem>
#include <QGraphicsEllipseItem>
#include <QDebug>
#include <QClipboard>
#include <QApplication>

ImageColorPicker::ImageColorPicker(QWidget *parent)
    : QWidget(parent)
    , m_ui(new Ui::ImageColorPicker)
    , m_graphics_scene(new QGraphicsScene())
    , m_item(new QGraphicsPixmapItem)
    , m_cursor(new QGraphicsEllipseItem(0,0,20,20))
    , m_moving(false)
{
    m_cursor->setBrush(QBrush(Qt::red, Qt::SolidPattern));
    m_ui->setupUi(this);
    setAcceptDrops(true);
    setMouseTracking(true);
    grabMouse();
    m_graphics_scene->addItem(m_item);
    m_graphics_scene->addItem(m_cursor);
    m_ui->graphicsView->setScene(m_graphics_scene);
    connect(&m_network_access_manager, SIGNAL (finished(QNetworkReply*)), SLOT(downloadFinished(QNetworkReply*)));
    
    addAction(m_ui->actionPaste);
}

ImageColorPicker::ImageColorPicker(QImage* image, QWidget* parent)
    : ImageColorPicker(parent)
{
    m_image = *image;
    if(m_item != 0) delete m_item;
}

ImageColorPicker::~ImageColorPicker()
{
    delete m_ui;
    delete m_graphics_scene;
}

void ImageColorPicker::dragEnterEvent(QDragEnterEvent* e)
{
    if(e->mimeData()->hasImage()) e->acceptProposedAction();
    if(e->mimeData()->hasUrls()) e->acceptProposedAction();
}

void ImageColorPicker::dropEvent(QDropEvent* e)
{
    if(e->mimeData()->hasImage())
    {
        m_image = qvariant_cast<QImage>(e->mimeData()->imageData());
        e->acceptProposedAction();
        emit(imageChanged());
    }
    else if(e->mimeData()->hasUrls())
    {
        QUrl firstUrl = e->mimeData()->urls().first();
        download(firstUrl);
        e->acceptProposedAction();
    }
}

void ImageColorPicker::imageChanged()
{
    m_item->setPixmap(QPixmap::fromImage(m_image));
    m_item->update();
    moveSplitter();
}

void ImageColorPicker::moveSplitter()
{
    m_ui->graphicsView->fitInView(m_image.rect(), Qt::KeepAspectRatio);
    update();
}

void ImageColorPicker::updateDot(QMouseEvent *e)
{
    m_cursor->setPos(m_ui->graphicsView->mapToScene(e->pos())-QPoint(10,10));
    QColor color = QColor(m_item->pixmap().toImage().pixel((m_ui->graphicsView->mapToScene(e->pos())).toPoint()));
    m_ui->label_5->setStyleSheet("background-color:"+color.name()+";");
    m_ui->lineEdit->setText(QString::number((float)color.red()/255.));
    m_ui->lineEdit_2->setText(QString::number((float)color.green()/255.));
    m_ui->lineEdit_3->setText(QString::number((float)color.blue()/255.));
    m_ui->lineEdit_4->setText(QString("vec3(%1,%2,%3)").arg((float)color.red()/255.,4,'f',2,' ').arg((float)color.green()/255.,4,'f',2,' ').arg((float)color.blue()/255.,4,'f',2,' '));
    m_ui->lineEdit_4->setFocus();
    m_ui->lineEdit_4->selectAll();
    m_ui->lineEdit_5->setText(color.name());
}


void ImageColorPicker::mousePressEvent(QMouseEvent* e)
{
    if(m_ui->graphicsView->rect().contains(e->pos()) && m_item != 0)
    {
        m_moving = true;
        updateDot(e);
    }
}

void ImageColorPicker::mouseReleaseEvent(QMouseEvent* e)
{
    m_moving = false;
}

void ImageColorPicker::mouseMoveEvent(QMouseEvent* e)
{
    if(m_moving) updateDot(e);
}

void ImageColorPicker::resizeEvent(QResizeEvent* e)
{
    emit(moveSplitter());
}

void ImageColorPicker::download(QUrl url)
{
    QNetworkRequest request(url);
    m_network_access_manager.get(request);
}

void ImageColorPicker::downloadFinished(QNetworkReply *reply)
{
    qDebug() << reply->readAll();
    m_image.loadFromData(reply->readAll());
    emit(imageChanged());
}

void ImageColorPicker::paste()
{
    const QClipboard *clipboard = QApplication::clipboard();
    const QMimeData *mimeData = clipboard->mimeData();

    if(mimeData->hasImage())
    {
        m_image = qvariant_cast<QImage>(mimeData->imageData());
        emit(imageChanged());
    }
}
