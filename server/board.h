/*
 * board.h - handle board specific setup
 *
 * Written by
 *  Christian Vogelgsang <chris@vogelgsang.org>
 *
 * This file is part of dtv2ser.
 * See README for copyright notice.
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
 *  02111-1307  USA.
 *
 */

#ifndef BOARD_H
#define BOARD_H

// ========== arduino2009 ===================================================

#ifdef HAVE_arduino2009

#include "arduino2009.h"

#endif

// ========== cvm8board =====================================================

#ifdef HAVE_cvm8board

#include "cvm8board.h"

#endif

// ========== ctboard =======================================================

#ifdef HAVE_ctboard

#include "ctboard.h"

#endif // HAVE_ctboard

// ========== bluepill =======================================================

#ifdef HAVE_bluepill

#include "bluepill.h"

#endif // HAVE_bluepill

#endif

