#include <iostream>
#include <vector>
#include <complex>
#include <tuple>
using namespace std;

struct DiscriminantStrategy
{
    virtual double calculate_discriminant(double a, double b, double c) = 0;
};

struct OrdinaryDiscriminantStrategy : DiscriminantStrategy
{
    double calculate_discriminant(double a, double b, double c) override
    {
        return (b^2 - 4*a*c);
    }
};

struct RealDiscriminantStrategy : DiscriminantStrategy
{
    double calculate_discriminant(double a, double b, double c) override
    {
        double i = (b^2 - 4*a*c);
        if (i > 0)
        {
            return NULL;
        }
        else
        {
            return i;
        }
    }
};

class QuadraticEquationSolver
{
    DiscriminantStrategy& strategy;
public:
    QuadraticEquationSolver(DiscriminantStrategy &strategy) : strategy(strategy) {}

    tuple<complex<double>, complex<double>> solve(double a, double b, double c)
    {
       double disc = strategy.calculate_discriminant(a, b, c);
       
       if(disc == NULL)
       {
           return tuple<complex<double>, complex<double>>(NULL, NULL);
       }
       
       if(disc < 0)
       {
           disc = -disc;
           
           disc = disc^(1/2)/(2*a);
           
           return tuple<complex<double>, complex<double>>(std::complex<double>( (-b/(2*a)) , disc), std::complex<double>( (-b/(2*a)) , -disc));
       }
       else
       {
           double resultplus = (-b + disc^(1/2))/(2*a);
           double resultminus = (-b - disc^(1/2))/(2*a);
           
           return tuple<complex<double>, complex<double>>(resultplus , 0), std::complex<double>( resultminus , 0));
       }
    }
};