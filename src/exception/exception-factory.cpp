/*
 * Copyright 2010,
 * François Bleibel,
 * Olivier Stasse,
 *
 * CNRS/AIST
 *
 * This file is part of sot-core.
 * sot-core is free software: you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public License
 * as published by the Free Software Foundation, either version 3 of
 * the License, or (at your option) any later version.
 * sot-core is distributed in the hope that it will be
 * useful, but WITHOUT ANY WARRANTY; without even the implied warranty
 * of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.  You should
 * have received a copy of the GNU Lesser General Public License along
 * with sot-core.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <sot/core/exception-factory.hh>
#include <sot/core/debug.hh>
#include <stdarg.h>
#include <cstdio>

using namespace dynamicgraph::sot;

/* --------------------------------------------------------------------- */
/* --- CLASS ----------------------------------------------------------- */
/* --------------------------------------------------------------------- */

const std::string ExceptionFactory::EXCEPTION_NAME = "Factory";

ExceptionFactory::
ExceptionFactory ( const ExceptionFactory::ErrorCodeEnum& errcode,
		      const std::string & msg )
  :ExceptionAbstract(errcode,msg)
{
  sotDEBUGF( 15,"Created with message <%s>.",msg.c_str());
  sotDEBUG( 1) <<"Created with message <%s>."<<msg<<std::endl;
}

ExceptionFactory::
ExceptionFactory ( const ExceptionFactory::ErrorCodeEnum& errcode,
			const std::string & msg,const char* format, ... )
  :ExceptionAbstract(errcode,msg)
{
  va_list args;
  va_start(args,format);

  const unsigned int SIZE = 256;
  char  buffer[SIZE];
  vsnprintf(buffer,SIZE,format,args);

  sotDEBUG(15) <<"Created "<<" with message <"
	       <<msg<<"> and buffer <"<<buffer<<">. "<<std::endl;

  message += buffer;

  va_end(args);

  sotDEBUG(1) << "Throw exception " << EXCEPTION_NAME << "[#" << errcode<<"]: " 
	      <<"<"<< message << ">."<<std::endl;

}


/*
 * Local variables:
 * c-basic-offset: 2
 * End:
 */
