# Copyright (C) 2019-2020  Learnershape and contributors

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from sqlalchemy import func,  Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from urllib.parse import urlparse

from . import Base


class Course(Base):
  __tablename__ = 'courses'
  id = Column(Integer, primary_key = True)
  excel_id = Column(Integer)
  name = Column(String)
  certificate = Column(String)
  type = Column(String)
  provider = Column(String)
  platform = Column(String)
  duration = Column(String)
  url = Column(String)
  specialisation  = Column(String)
  type2  = Column(String)
  duration_code  = Column(String)
  free  = Column(String)
  start = Column(String)
  created_at = Column(DateTime, nullable=False, server_default=func.now())
  modified_at = Column(DateTime, nullable=False, server_default=func.now(), server_onupdate=func.now())
  alt_id = Column(Text)
  description = Column(Text)
  short_description = Column(Text)
  tag = Column(Text)
  weekly_effort = Column(Float)


  def __setattr__(self, name, value):
    """Altered to ensure bad URLs are not added to the database"""
    if name == 'url':
      u = urlparse(value)
      if u.netloc == '':
        raise Exception('Invalid URL supplied', value)
    super().__setattr__(name, value)
