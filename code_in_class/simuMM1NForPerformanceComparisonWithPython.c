
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <sys/time.h>

enum typeEvt {evtArrival, evtService};

struct evt
{
   enum typeEvt nature;
   double date;
};

struct scheduler
{
  struct scheduler* next;
  struct evt* e;
};

//Function to insert a event in the scheduler:
void insertEvtInScheduler(l, e, schedSize)
struct scheduler **l;
struct evt *e;
long int *schedSize;
{
    struct scheduler *l_new;
    l_new = malloc(sizeof(struct scheduler));
    if (l_new == NULL) {printf("Memory full\n");exit(EXIT_FAILURE);}

    struct scheduler *p_tmp = NULL;
    struct scheduler *p_l = *l;
    l_new->e = e;
    l_new->next = NULL;

    while (p_l != NULL && (p_l->e)->date <= e->date)
    {
        p_tmp = p_l;
        p_l = p_l->next;
    }
    l_new->next = p_l;
    if (p_tmp != NULL) p_tmp->next = l_new;
    else *l = l_new;
    
    (*schedSize) ++;

    return ;
}

//Function returning a random number exponentially distributed with parameter lambda:
double expo(lambda)
double lambda;
{
  // You can use drand48() which returns a random number uniformly distributed (and uncorrelated) on [0;1]

  return(-log(1.0 - drand48()) / lambda);
}

//Commands to execute at an end of service:
void endOfService(now, sched, mu, queue, schedSize)
double now, mu;
int *queue;
struct scheduler **sched;
long int *schedSize;
{
  struct evt *e;

  (*queue)--;

  if (*queue > 0) 
  {
    e = malloc(sizeof(struct evt));
    //...TBC...
    e->nature = evtService;
    e->date = now + expo(mu);

    insertEvtInScheduler(sched,e, schedSize);
  }
  return;
}

//Unuseful function for the exercise, but which may be used to monitor the scheduler:
void printScheduler(sched)
struct scheduler *sched;
{
  printf("--------------------\n");
  while (sched !=NULL)
  {
    if (sched->e->nature == evtArrival) printf("%le evtArrival, ",sched->e->date);
    else if (sched->e->nature == evtService) printf("%le evtService, ", sched->e->date);
    else printf("Error while printing scheduler\n");
    printf("\n");
    sched = sched->next;
  }
  printf("--------------------\n");
  return;
}

//Command to execute to simulate a departure from the source:
void arrival(now, sched, lambda, mu, queue, schedSize, nbRejections, queueMaxSize, nbArrivals)
double now, lambda, mu;
int *queue, *nbRejections, *queueMaxSize, *nbArrivals;
struct scheduler **sched;
long int *schedSize;
{
  struct evt *e;
  
  (*nbArrivals)++;
  if ((*queue) < (*queueMaxSize)) {
	  (*queue)++; 
  } else {
	  (*nbRejections)++;
  }
  
  e = malloc(sizeof(struct evt));
  //...TBC...
  e->nature = evtArrival;
e->date = now + expo(lambda); 

  insertEvtInScheduler(sched,e,schedSize);

  if (*queue == 1) 
  {
    e = malloc(sizeof(struct evt));
    //...TBC...
    e->nature = evtService;
e->date = now + expo(mu);

    insertEvtInScheduler(sched,e,schedSize);
  }

  return;
}

int main(argc,argv) 
int argc;
char **argv;
{

  struct scheduler *sched=NULL, *a;
  struct evt *firstArrival, *e;
  double lambda, mu, duration, now;
  int queue, nbRejections, queueMaxCapacity, nbArrivals;
  long int schedSize;


  if ( argc != 5 ) 
  {
    fprintf(stderr, "Usage: %s lambda mu duration queueMaxCapacity\n",argv[0]);
    exit(1);
  }

  //The following lines will be used to calculate the execution duration:
  double t0 = clock();
  struct timeval tv;
  gettimeofday(&tv, NULL);
  

  //We get the parameters of the simulation:
  lambda = atof(argv[1]);
  mu = atof(argv[2]);
  duration = atof(argv[3]);
  queueMaxCapacity = atoi(argv[4]);

  queue = 0;
  schedSize = 0;
  nbRejections = 0;
  nbArrivals = 0;
  now = 0; // now is the simulated time

  //Initilisation of the simulation with one arrival from the Poisson source:
  firstArrival = malloc(sizeof(struct evt));
  firstArrival->nature = evtArrival;
  firstArrival->date = expo(lambda);
  
  insertEvtInScheduler(&sched,firstArrival,&schedSize);

  //Let's run the simulation:
  do
  {
    //Get the event at the top of the scheduler and advance the time:
    e = sched->e;
    a = sched->next;
    free(sched);
    schedSize --;
    sched = a;
    //now = ...TBC...;
    now = e->date;


    //Execute the event:
    if (e->nature == evtArrival) arrival(now, &sched, lambda, mu, &queue, &schedSize, &nbRejections, &queueMaxCapacity, &nbArrivals);
    else if (e->nature == evtService) endOfService(now, &sched, mu, &queue, &schedSize);
    else 
    {
      printf("Error with the nature of the event\n");
      exit(0);
    }
    //Deallocation of the event:
    free(e);
  } while (now <= duration || e == NULL);

  //The execution time is estimated two different ways:
  printf("Loss rate: %le\nExecution duration: %le\n",nbRejections*1.0/nbArrivals, (clock()-t0)/CLOCKS_PER_SEC);
  struct timeval tv2;
  gettimeofday(&tv2, NULL);
  printf("Execution duration: %lf\n", (double)(tv2.tv_sec-tv.tv_sec+(tv2.tv_usec-tv.tv_usec)*0.000001));

  return(1);
}
