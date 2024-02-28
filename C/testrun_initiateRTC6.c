#include <windows.h>
#include <stdio.h>
#include <conio.h>
#include "RTC6impl.h"

void terminateDLL();

UINT ErrorCode;

void __cdecl main()
{
    printf( "Initilising the DLL\n\n");

    ErrorCode = init_rtc6_dll();
    (void) select_rtc(1);
    reset_error( -1 );
    config_list( 4000, 4000 );

    terminateDLL();
    return;
}

void terminateDLL()
{
    printf( "Press any key to shut down\n");
    while( !kbhit() );
    (void) getch();
    printf( "\n" );
    free_rtc6_dll();
}

int main() {
    ErrorCode = init_rtc6_dll();
    if ( ErrorCode )
    {
        UINT RTC6CountCards = rtc6_count_cards();
        if ( RTC6CountCards )
        {
            UINT AccError = 0;
            for ( UINT i = 1; i <= RTC6CountCards; i++ )
            {
                UINT Error = n_get_last_error( i );
                if ( Error != 0 )
                {
                    AccError |= Error;
                    UINT SerialNumber = n_get_serial_number ( i );
                    printf( "RTC6 Board number %d serial - %d: Error %d detected\n",
                                i, SerialNumber, Error );
                    n_reset_error( i, Error );
                }
            }
            if ( AccError )
            {
                free_rtc6_dll();
                return 0;
            }
        }
        else
        {
            printf( "Initilising the DLL: Error %d detected\n", ErrorCode );
            free_rtc6_dll();
            return 0;
        }
    }
    else
    {
        const UINT SerialNumberOfDesiredBoard = 0; // replace 0 with the desired serial number
        const UINT RTC6CountCards = rtc6_count_cards();
        UINT InternalNumberOfDesiredBoard = 0;
        for ( UINT i = 1; i <= RTC6CountCards; i++)
        {
            if ( n_get_serial_number( i ) == SerialNumberOfDesiredBoard )
            {
                InternalNumberOfDesiredBoard = i;
            }
        }
        if ( InternalNumberOfDesiredBoard == 0)
        {
            printf( "RTC6 board with serial number %d not detected...\n", SerialNumberOfDesiredBoard);
            free_rtc6_dll();
            return 0;
        }
        if ( InternalNumberOfDesiredBoard != select_rtc( InternalNumberOfDesiredBoard ) )
        {
            ErrorCode = n_get_last_error( InternalNumberOfDesiredBoard );
            if ( ErrorCode & 256 )
            {
                if ( ErrorCode = n_load_program_file( InternalNumberOfDesiredBoard, 0 ) )
                {
                    printf ( "n_load_program_file returned error code %d\n", ErrorCode );
                }
            }
            else
            {
                printf( "No access to RTC6 board with serial number %d\n", SerialNumberOfDesiredBoard );
                free_rtc6_dll();
                return 0;
            }
            if ( ErrorCode )
            {
                printf( "No access to RTC6 board with serial number %d\n", SerialNumberOfDesiredBoard );
                free_rtc6_dll();
                return 0;
            }
            else
            {
                (void) select_rtc( InternalNumberOfDesiredBoard );
            }
        }
    }
    return 0;
}
