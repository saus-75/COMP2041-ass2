#!/usr/bin/perl -w

# written by andrewt@cse.unsw.edu.au September 2016
# as a starting point for COMP2041/9041 assignment 2
# http://cgi.cse.unsw.edu.au/~cs2041/assignments/matelook/

use CGI qw/:all/;
use CGI::Carp qw/fatalsToBrowser warningsToBrowser/;
use CGI::Cookie;

sub main() {
    # print start of HTML ASAP to assist debugging if there is an error in the script
    print page_header();
    
    # Now tell CGI::Carp to embed any warning in HTML
    warningsToBrowser(1);
    
    # define some global variables
    $debug = 1;
    $users_dir = "dataset-medium";
    create_database();

    $result = param('search_bar')||undef;
    $username = param('username')||undef;
    $password = param('password')||undef;

    $rcvd = $ENV{'HTTP_COOKIE'};
    if (defined $rcvd){
        $rcvd =~ s/Login=//g;
        @cookie = split(/&/, $rcvd);
        $username = $cookie[0];
        $password = $cookie[1];
    }
    print user_login();

    if (defined $result){
        print user_search();
    } else {
        print "<div class=\"main\">";
        print user_page();
        print "</div>";

}
    # print user_login();
    print page_footer();
    print page_trailer();
}

sub create_database {
    %userDatabase;
    my @users = sort(glob("$users_dir/*"));

    for (my $j = 0; $j < 0+@users; $j++){
        my $scope = $users[$j];
        $scope =~ s/.*\///g;
        $userDatabase{$scope} = $j;
    }
    return;
}
#
# Show unformatted details for user "n".
# Increment parameter n and store it as a hidden variable
#
sub user_page {
    my $n = param('n') || 0;
    my @users = sort(glob("$users_dir/*"));

    $n = $n % @users;
    my $user_to_show  = $users[$n % @users];
    my $details_filename = "$user_to_show/user.txt";
    $user_pic = "$user_to_show/profile.jpg";
    my @user_comments = sort {$b cmp $a} (glob("$user_to_show/posts/*"));
    print "<div class=\"user_pane\">";
    print "<div class=\"user_info_space\">";
    print <<eof;
    <div class="profile_picture">
        <img class="profile_picture" src="$user_pic" alt="Profile Picture">
    </div>
eof
    open my $p, "$details_filename" or die "can not open $details_filename: $!";
    foreach my $line (<$p>){
        if ($line =~ /(home_latitude|home_longitude|courses|password|email)\=/){
            push @hidden_info, $line;
        } else {
            $line =~ s/_/ /g;
            $line =~ s/([\w']+)/\u\L$1/g;
            $line =~ s/Z([0-9]*)/z$1/g;
            $line =~ s/=/<br>/g;
            push @open_info, $line;
        }
    }
    $user = join "<p class=\"matelook_user_details\">", sort @open_info;
    chomp $user;
    $user =~ s/\[|\]/ /g;
    $user =~ s/^/<p class =\"matelook_user_details\">/g;
    close $p;
    my $next_user = $n + 1;

    print <<eof;
    <div class ="matelook_user_details">
    $user
    </div>
    </div>
eof

    print "<div class=\"wall\">";
        foreach my $post (@user_comments){
            $text = "$post/post.txt";
            open my $q, "$text" or die "cannot ope $text: $!";
            my $txtpost = undef;
            print "<p class = \"post\">";
            foreach my $txt (<$q>){
                if ($txt =~ /message=/){
                    $txt =~ s/\\n/\n/g;
                    $txt =~ s/message=//g;
                    $txtpost = $txt;
                } elsif ($txt =~ /time=/){
                    $txt =~ s/time=//g;
                    $txt =~ s/T/ /g;
                    $txt =~ s/\+.*//g;
                    chomp $txt;
                    print "$txt &nbsp; &nbsp;";
                }
            }
            close $q;
            print $txtpost;
            print "</p>";
        }
    print "</div>";

    print <<eof;
    <div class="matelook_button">
    <form>
        <input type="hidden" name="n" value="$next_user">
        <input type="submit" value="Next user" class="matelook_button">
    </form>
    </div>
    </div>
eof
    print friend_list($details_filename);
    return;
}

#
# Gets the friend list and make it so that it can be clicked on
#
sub friend_list {
    my $text = shift;
    open my $p, "$text" or die "can not open $text: $!";

    foreach my $list (<$p>){
        if ($list =~ /mates=/){
            $list =~ s/(mates=|\[|\])//g;
            @friends = split (/,/, $list);
        }
    }
    close $p;
    print "<div class=\"friend_pane\">";
    print "<table class=\"friend_img\">";

    for (@friends){
        my $x = $_;
        $x =~ s/\s*//g;
        my $value = $userDatabase{$x};
        my $img = "$users_dir/$x/profile.jpg";
        my $deet = "$users_dir/$x/user.txt";
        open my $q, "$deet" or die "can not open $deet: $!";
        foreach my $line (<$q>){
            if ($line =~ /full_name=/){
                $line =~ s/full_name=//g;
                print "<tr>";
                print "<th><a href=\"http://cgi.cse.unsw.edu.au/~z5062534/ass2/matelook.cgi?n=$value\">
                <img class=\"friend_img\" src=\"$img\" alt=\"Friends Picture\"></a></th>";
                print "<th><a href=\"http://cgi.cse.unsw.edu.au/~z5062534/ass2/matelook.cgi?n=$value\">$line</a></th>";
                print "</tr>";
            }
        }
        close $q;
    }
    print "</table>";
    print "</div>";
    return;
}

#
# Friend Searcher
#
sub user_search {
    print "<div class=\"search_pane\">";
    my $flag = 0;
    if (defined $result){
        print "<table class=\"search_result\"> Result:";
        my @users = sort(glob("$users_dir/*"));
        foreach my $user (@users){
            my $img = "$user/profile.jpg";
            my $details = "$user/user.txt";
            open my $p, "$details" or die "can not open $details: $!";
            foreach my $line (<$p>){
                if ($line =~ /full_name=/){
                    $line =~ s/full_name=//g;
                    if(index(lc($line), lc($result)) != -1){
                        my $temp = $user;
                        $temp =~ s/^.*\///g;
                        my $value = $userDatabase{$temp};
                        print "<tr>";
                        print "<th><a href=\"http://cgi.cse.unsw.edu.au/~z5062534/ass2/matelook.cgi?n= $value \">
                        <img class=\"search_img\" src=\"$img\" alt=\"Friends Picture\"></a></th>";
                        print "<th><a href=\"http://cgi.cse.unsw.edu.au/~z5062534/ass2/matelook.cgi?n= $value \">$line</a></th>";
                        print "</tr>";
                        $flag = 1;
                        last;
                    }
                }
            }
            close $p;
        }
        print "</table>";
        if ($flag == 0){
            print "<p> No Results Found </p>";
        }
        print "</div>";
    }
    return;
}

#
# Login and Logout
#
sub user_login {
    my $user_flag = 0;
    if (defined $username && defined $password){
        my @users = sort(glob("$users_dir/*"));

        for (@users){
            my $usercheck = $_;
            $usercheck =~ s/.*\///g;
            if ($usercheck eq $username){
                $user_flag = 1;
                $passcheck = "$users_dir/$usercheck/user.txt";

                open my $p, "$passcheck" or die "can not open $passcheck: $!";

                foreach my $line (<$p>){
                    if ($line =~ /password=/){
                        chomp $line;
                        $line =~ s/(password=| )//g;
                        if ($line eq $password){
                            $cookie = CGI::Cookie->new(-name=>'Login', -value=>[$username, $password]);
                            print "<meta http-equiv=\"set-cookie\" content=\"$cookie\">";
                        } else {
                            print "Password incorrect!";
                            param(-name =>'username', -values => '');
                            param(-name =>'password', -values => '');
                            print start_form, "\n";
                            print "Username:\n", textfield('username'), "\n";
                            print "Password:\n", textfield('password'), "\n";
                            print submit(value => Login), "\n";
                            print end_form, "\n"; 
                        }
                        last;
                    }
                }
                close $p;
            }
        }
        if ($user_flag == 0){
            print "User Does Not Exist!";
            param(-name =>'username', -values => '');
            param(-name =>'password', -values => '');
            print start_form, "\n";
            print "Username:\n", textfield('username'), "\n";
            print "Password:\n", textfield('password'), "\n";
            print submit(value => Login), "\n";
            print end_form, "\n"; 
        }
    } elsif (defined $username && !$password){
        print start_form, "\n";
        print hidden('username', "$username");
        print "Password:\n", textfield('password'), "\n";
        print submit(value => Login), "\n";
        print end_form, "\n";
    } elsif (!$username && defined $password){
        print start_form, "\n";
        print hidden('password', "$password");
        print "Username:\n", textfield('username'), "\n";
        print submit(value => Login), "\n";
        print end_form, "\n";
    } else {
        print start_form, "\n";
        print "Username:\n", textfield('username'), "\n";
        print "Password:\n", textfield('password'), "\n";
        print submit(value => Login), "\n";
        print end_form, "\n";     
    }
    return;
}

#
# HTML placed at the top of every page
#
sub page_header {
    print <<eof;
Content-Type: text/html;charset=utf-8

<!DOCTYPE html>
<html lang="en">
<head>
<title>\xF0\x9F\x92\xAFLITBOOK\xF0\x9F\x92\xAF</title>
<link href="matelook.css" rel="stylesheet">
<link rel="shortcut icon" href="favicon.ico" type="image/x-icon">
</head>
<body>
<div class="matelook_heading">
    <form class="search_bar">
        <input type="textfield" name="search_bar" class="search">
        <input type="submit" value="search" class="search">
    </form class="search_bar">
    <p class="title"><a href="http://cgi.cse.unsw.edu.au/~z5062534/ass2/matelook.cgi" style="text-decoration: none;color: inherit;">\xF0\x9F\x94\xA5\xF0\x9F\x92\xAFLITBOOK\xF0\x9F\x94\xA5\xF0\x9F\x92\xAF</a></p>
</div>
eof
    return;
}


#
# A footer for the memes
# and also my name
#
sub page_footer {
    return <<eof
<footer class="footer_note">
    <p> <h4>Created by: George Chieng</h4> Powered by: My Tears&trade; All Rights Reserved.</p>
</footer>
eof
}

#
# HTML placed at the bottom of every page
# It includes all supplied parameter values as a HTML comment
# if global variable $debug is set
#
sub page_trailer {
    my $html = "";
    $html .= join("", map("<!-- $_=".param($_)." -->\n", param())) if $debug;
    $html .= end_html;
    return $html;
}

main();
