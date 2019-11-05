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

#ifndef IMAGE_COLOR_PICKER_H
#define IMAGE_COLOR_PICKER_H

#include <QWidget>
#include <QImage>
#include <QGraphicsScene>
#include <QDragEnterEvent>
#include <QDropEvent>
#include <QMouseEvent>
#include <QResizeEvent>

namespace Ui { class ImageColorPicker; }

class ImageColorPicker : public QWidget
{
    Q_OBJECT
    
public:
    ImageColorPicker(QWidget * parent = 0);
    ImageColorPicker(QImage *image, QWidget * parent = 0);
    virtual ~ImageColorPicker();
    
private slots:
    void imageChanged();
    void moveSplitter();
    
private:
    void dragEnterEvent(QDragEnterEvent *e);
    void dropEvent(QDropEvent *e);
    void mousePressEvent(QMouseEvent *e);
    void mouseMoveEvent(QMouseEvent *e);
    void mouseReleaseEvent(QMouseEvent *e);
    void resizeEvent(QResizeEvent *e);
    
    void clicked();
    void updateDot(QMouseEvent *e);
    
private:
    QImage m_image;
    QGraphicsScene *m_graphics_scene;
    QGraphicsPixmapItem *m_item;
    Ui::ImageColorPicker *m_ui;
    QGraphicsEllipseItem *m_cursor;
    bool m_moving;
};

#endif
