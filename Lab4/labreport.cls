\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{labreport}[2026/02/09 Custom Lab Report Class]

% Base class
\LoadClass[12pt,a4paper]{article}

% Packages
\RequirePackage[utf8]{inputenc}
\RequirePackage[UKenglish]{babel} % UK English
\RequirePackage{geometry}
\RequirePackage{graphicx}
\RequirePackage{amsmath,amssymb}
\RequirePackage{listings}
\RequirePackage{xcolor}
\RequirePackage{hyperref}
\RequirePackage{booktabs}
\RequirePackage{float}
\RequirePackage{caption}
\RequirePackage{subcaption}
\RequirePackage{fancyhdr}
\RequirePackage{titlesec}
\RequirePackage{mathptmx} % Times New Roman font

% Page geometry defaults
\geometry{
    left=25mm,
    right=25mm,
    top=25mm,
    bottom=25mm,
    headheight=15pt
}

% Header and footer
\pagestyle{fancy}
\fancyhf{}
\rhead{\thepage}
\lhead{\leftmark}
\renewcommand{\headrulewidth}{0.4pt}

% Python code listing style
\lstdefinestyle{python}{
    language=Python,
    basicstyle=\ttfamily\small,
    keywordstyle=\color{blue}\bfseries,
    commentstyle=\color{gray}\itshape,
    stringstyle=\color{red},
    showstringspaces=false,
    breaklines=true,
    frame=single,
    numbers=left,
    numberstyle=\tiny\color{gray},
    backgroundcolor=\color{gray!10}
}

% Hyperref setup
\hypersetup{
    colorlinks=true,
    linkcolor=black,
    filecolor=magenta,      
    urlcolor=blue,
    citecolor=black
}

% Title page command
% #1 lab number, #2 title, #3 elaborated left, #4 elaborated right, #5 verified
\newcommand{\labtitle}[5]{%
    \begin{titlepage}
        \centering
        \large

        \vspace*{1.5cm}

        {\bfseries Ministerul Educației și Cercetării al Republicii Moldova\par}
        \vspace{0.3cm}
        {\bfseries Universitatea Tehnică a Moldovei\par}
        \vspace{0.3cm}
        {\bfseries Facultatea Calculatoare, Informatică și Microelectronică\par}

        \vspace{4.5cm}

        {Laboratory Work #1:\par}
        \vspace{0.5cm}
        {#2\par}

        \vfill

        % ----- Elaborated -----
        \noindent
        \begin{minipage}{0.48\textwidth}
            {\raggedright Elaborated:}\\[0.4cm]
            {\raggedright #3}
        \end{minipage}
        \hfill
        \makebox[0.48\textwidth][r]{#4}

        \vspace{1.2cm}

        % ----- Verified -----
        \noindent
        \begin{minipage}{0.48\textwidth}
            {\raggedright Verified:}
        \end{minipage}
        \hfill
        \makebox[0.48\textwidth][r]{#5}

        \vspace{2cm}

        {Chișinău -- \the\year\par}

    \end{titlepage}
}
