import logging
import os
import sys
import structlog

def configure_logging(level:str | None = None , json_output:bool | None = None) -> None:
    """Idempotent global logger configuration.
    Resolution for each setting: explicit arg > env > default
    LOG_LEVEL  - stdlib level name (debug/info/warning/...).Default: info .
    Log_JSON   - force JSON output. Default: JSON if stderr is non -TTY (CI/prod) 

    """


    log_level_name = (level or os.environ.get("LOG_LEVEL", "info")).upper() 
    log_level = getattr(logging , log_level_name , logging.INFO)

    if json_output is None:
        json_output = (
            os.environ.get("LOG_JSON","").lower() in {"1" , "yes" ,"true"}
            or not sys.stderr.isatty()
        )

    renderer = (
        structlog.processors.JSONRenderer()  if json_output else structlog.dev.ConsoleRenderer
    )

    structlog.configure(Processors =[structlog.contextvars.merge_contextvars,
                        structlog.processors.add_log_level,
                        structlog.processors.TimeStamper(fmt="iso"),
                        renderer
                                     ],
                                     wrapper_class = structlog.make_filtering_bound_logger,
                                     cache_logger_on_first_use= True
                                     
                                     
                                     ) 
    logging.basicConfig(level=log_level , format="%(message)s" , stream = sys.stderr)


if __name__ =="__main__":

 #console Rendering(json_oujtput = false)
    configure_logging(level="info", json_output =False)
    log = structlog.get_logger() 
    log.info("ticket_classified",ticket_id ="TKT-10001",
            priority ="urgent",
            category="billing",
            confidence=0.94 ,
            )
    log.warning("enrichment_slow" ,
                ticket_id ="TKT-10001",
                duration_ms = 3420)