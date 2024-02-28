#include <windows.h>
#include <stdio.h>
#include <conio.h>
#include "RTC6impl.h"

UINT ErrorCode;

void terminateDLL()
{
    printf("Press any key to shut down\n");
    while (!kbhit())
        ;
    (void)getch();
    printf("\n");
    free_rtc6_dll();
}

void __cdecl main(void*, void*)
{
    printf("Initilising the DLL\n\n");

    ErrorCode = init_rtc6_dll();
    if (ErrorCode)
    {
        UINT RTC6CountCards = rtc6_count_cards();
        if (RTC6CountCards)
        {
            UINT AccError = 0;
            for (UINT i = 1; i <= RTC6CountCards; i++)
            {
                UINT Error = n_get_last_error(i);
                if (Error != 0)
                {
                    AccError |= Error;
                    UINT SerialNumber = n_get_serial_number(i);
                    printf("RTC6 Board number %d serial - %d: Error %d detected\n",
                           i, SerialNumber, Error);
                    n_reset_error(i, Error);
                }
            }
            if (AccError)
            {
                free_rtc6_dll();
                return;
            }
        }
        else
        {
            printf("Initilising the DLL: Error %d detected\n", ErrorCode);
            free_rtc6_dll();
            return;
        }
    }
    else
    {
        const UINT SerialNumberOfDesiredBoard = 344466;
        const UINT RTC6CountCards = rtc6_count_cards();
        UINT InternalNumberOfDesiredBoard = 0;
        UINT RCT6SerialNumber = 0;
        for (UINT i = 1; i <= RTC6CountCards; i++)
        {
            RCT6SerialNumber = n_get_serial_number(1);
            printf("Serial: %d\n\n", RCT6SerialNumber);
            if (n_get_serial_number(i) == SerialNumberOfDesiredBoard)
            {
                InternalNumberOfDesiredBoard = i;
            }
        }
        if (InternalNumberOfDesiredBoard == 0)
        {
            printf("RTC6 board with serial number %d not detected...\n", SerialNumberOfDesiredBoard);
            free_rtc6_dll();
            return;
        }
        if (InternalNumberOfDesiredBoard != select_rtc(InternalNumberOfDesiredBoard))
        {
            ErrorCode = n_get_last_error(InternalNumberOfDesiredBoard);
            if (ErrorCode & 256)
            {
                if (ErrorCode = n_load_program_file(InternalNumberOfDesiredBoard, 0))
                {
                    printf("n_load_program_file returned error code %d\n", ErrorCode);
                }
            }
            else
            {
                printf("No access to RTC6 board with serial number %d\n", SerialNumberOfDesiredBoard);
                free_rtc6_dll();
                return;
            }
            if (ErrorCode)
            {
                printf("No access to RTC6 board with serial number %d\n", SerialNumberOfDesiredBoard);
                free_rtc6_dll();
                return;
            }
        }
        else
        {
            printf("Connecting to card serial %d\n\n", SerialNumberOfDesiredBoard);
            UINT32 CardNo = select_rtc(InternalNumberOfDesiredBoard);
            if (CardNo)
            {
                printf("%d", CardNo);
            }
        }
    }
    reset_error(-1);
    config_list(4000, 4000);
    ErrorCode = load_correction_file("C:\\Program Files (x86)\\SCANLAB\\D2_2034.ct5", 1, 2);
    if (ErrorCode)
    {
        printf("Correction file loading error: %d\n", ErrorCode);
        free_rtc6_dll();
        return;
    }
    else
    {
        printf("Correction file loaded\n\n");
    }
    select_cor_table(1,0);
    set_laser_mode(0); // page 174
    set_laser_control( 0x18 ); //  page ?
    // first make a list of params to save under list 1
    set_start_list(1);
    set_standby_list( 100, 1); // do I even need this?
    set_scanner_delays(25,10,5);
    set_jump_speed(100);
    set_mark_speed(10);
    set_laser_pulses(800, 400);
    set_laser_delays(100,100);
    set_end_of_list();
    execute_list(1);

    UINT32 loadList = load_list(1,0);
    printf("Loaded list %d\n\n", loadList);
    jump_abs(0,0); 
    laser_on_list(5); //hole in middle
    jump_abs(-20000, -20000);
    mark_abs(-20000, 20000);
    mark_abs(20000, 20000);
    mark_abs(20000, -20000);
    mark_abs(-20000, -20000); // square
    jump_abs(0, -10000);
    arc_abs(0,0, 360); // circle
    set_end_of_list();
    execute_list(1);
    terminateDLL();
    return;
}
