#!C:/Perl64/bin/perl.exe
# written by andrewt@cse.unsw.edu.au October 2013
# as a starting point for COMP2041 assignment 2
# http://www.cse.unsw.edu.au/~cs2041/assignments/mekong/

use CGI qw/:all/;

$debug = 0;
$| = 1;

if (!@ARGV) {
	# run as a CGI script
	cgi_main();
} else {
	# for debugging purposes run from the command line
	console_main();
}
exit(0);

sub cgi_main {
	my $username = param('username');

	print page_header();
    print navbar($username);

    set_global_variables();
	read_books($books_file);

	my $search_terms = param('search_terms');
    my $new_username = param('new_username');
    my $password = param('password');
    my $purchase = param('purchase');
    my $learn = param('learn');
    my $view = param('view');
    my $logout = param('logout');
    my ($login, $name, $street, $city, $state, $postcode, $email) = (param('login'), param('name'), param('street'), param('city'), param('state'), param('postcode'), param('email'));
    if (defined $search_terms) {
		print search_results($search_terms);
    } elsif (defined $purchase) {
        if (!defined $username || $username eq "") {
            print(generic_form("Please log in before you buy stuff!"));
        } elsif (add_basket($username, $purchase)) {
            print(generic_form("Well done on making your purchase!"));
        } else {
            print(generic_form("$last_error"));
        }
    } elsif (defined $learn) {
        print(generic_form("Mekong was made by Davy Mao from COMP2041"));
    } elsif (defined $view) {
        if ($view eq "cart") {
            if (!defined $username || $username eq "") {
                print(generic_form("Please log in before you buy stuff!"));
            } else {
                print(basket_results($username));
            }
        } else { # view order
        }
    } elsif (defined $logout) {
        $username = "";
        print(generic_form("You have been logged out. Thank you for shopping at Mekong!"));
    } elsif (defined $name) {
        if (new_account($login, $password, $name, $street, $city, $state, $postcode, $email)) {
            print(user_form($username));
        } else {
            print(new_user_form("error"));
        }
    } elsif (defined $password) {
        if (authenticate(($username, $password))) {
            print user_form($username);
        } else {
            print(guest_home($last_error));
        }
	} elsif (defined $new_username) {
        print(new_user_form($new_username));
    } elsif (defined $username && $username ne "") {
        print(user_form($username));
    } else {
		print guest_home();
	}
	
   
	print page_trailer();
}

# the home page for non-logged-in users	
sub guest_home {
	return <<eof;
    <div class="jumbotron">
        <div style="margin-left: 10%; float: left; width: 35%">
            <h1>Welcome to Mekong!</h1>
            <p>Mekong is a great website that makes buying books a fun experience!</p>
            <p>Make sure to check out some of the <a href="?search_terms=cool book"><b>top-ranked releases!</b></a></p>
            <br/>
            <p><a href="?learn=true"><button class="btn btn-primary btn-lg" role="button">Learn more about Mekong</button></a></p>
        </div>
        <div style="margin-left: 50%; width: 300px">
            <div class="panel panel-default panel-primary">
                <div class="panel-heading">
                    <h3 class="panel-title" style="font-size:20px">
                        <i class="glyphicon glyphicon-arrow-right"></i>
                        <b>Login to Mekong!</b>
                    </h3>
                </div>
                <div class="panel-body">
                    <form role="form" method="POST" action="?login=true">
                        <h5 style="color: red">@_</h4>
                        <div class="form-group">
                            <label for="username">Username: </label>
                            <input type="text" class="form-control" name="username" size=16></input>
                        </div>
                        <div class="form-group">
                            <label for="password">Password: </label>
                            <input type="password" class="form-control" name="password" size=16></input>
                        </div>
                        <button type="submit" class="btn btn-primary"><b>Login</b></button>
                    </form>
                </div>
            </div>
            <h2>Are you new to Mekong?</h2>
            <div class="panel panel-default panel-primary">
                <div class="panel-heading">
                    <h3 class="panel-title" style="font-size:20px">
                        <i class="glyphicon glyphicon-asterisk"></i>
                        <b>Make a new account!</b>
                    </h3>
                </div>
                <div class="panel-body">
                    <form role="form" method="POST" action="?">
                        <div class="form-group">
                            <label for="username">Your username: </label>
                            <input type="text" class="form-control" name="new_username" size=16></input>
                        </div>
                        <button type="submit" class="btn btn-success"><b>Make a new account!</b></button>
                    </form>
                </div>
            </div>
        </div>
    </div>

eof
}

sub user_form {
    return <<eof;
    <div style="margin-left:8%">
    <h1>Welcome back, @_!</h1>
    <h2>Here are some books you might be interested in.</h2>
    
    <h2>Or alternatively, you might want to search for you own book above.</h2>
    </div>
eof
}

sub generic_form {
    return <<eof;
    <br/>
    <div style="margin-left: 10%; width: 70%">
        <div class="alert alert-info">@_</div>
        <form method="POST" action="?">
            <button type="submit" class="btn btn-info">Back to Home</button>
            <input type="hidden" value="$username" name="username">
        </form>
    </div>
eof

}

sub new_user_form {
    my $username = @_[0];
    $formText = <<eof;
    <div class="panel panel-default" style="margin-left: 8%; width: 300px; margin-top: 20px">
    <div class="panel-body">
    <form role="form" method="POST" action="?username=$username">

eof

    if ($username eq "error") {
        our $last_error;
        $formText .= <<eof;
        <h5 style="color: red">$last_error</h4>
eof
    }
    our %new_account_rows;
    foreach my $text (@new_account_rows) {
        my ($name, $label) = split(m/\|/, $text);
        if ($name eq "login") {
            $formText .= <<eof;
            <div class="form-group">
                <label for="$name">$label</label>
                <input type="text" name="$name" value="$username">
            </div>

eof
        } elsif ($name eq "password") {
            $formText .= <<eof;
            <div class="form-group">
                <label for="$name">$label</label>
                <input type="password" name="$name" value="$username">
            </div>
eof

        } else {
         $formText .= <<eof;
        <div class="form-group">
            <label for="$name">$label</label>
            <input type="text" name="$name">
        </div>

eof

        }
    }
    
    $formText .= <<eof;
    <input type="submit" value="Make my new account!">
    </form>
    </div>
    </div>

eof
    return $formText;
}

# ascii display of search results
sub search_results {
	my ($search_terms) = @_[0];
    my @matching_isbns = search_books($search_terms);

	my $htmlHeader = <<eof;
    <div style="margin-left: 10%">
        <h2>Search results for $search_terms:</h2>
    </div>
    <table class="table table-hover" style="margin-left: 10%; width:70%">
    <thead>
        <tr>
            <th>Book</th>
            <th>Authors</th>
            <th>Title</th>
            <th>Price</th>
            <th>Add to cart</th>
            <th>
        </tr>
    </thead>
    <tbody>

eof

    my $resultTable = "";
    foreach my $isbn (@matching_isbns) {
        my $price = $book_details{$isbn}{price};
        my $title = $book_details{$isbn}{title};
        my $author = $book_details{$isbn}{authors};
        my $imageURL = $book_details{$isbn}{mediumimageurl};
        my $imageHeight = $book_details{$isbn}{mediumimageheight};
        my $imageWidth = $book_details{$isbn}{mediumimagewidth};
        $resultTable .= <<eof;
        <tr>
            <td>
                <image src=$imageURL width=$imageWidth height=$imageHeight>
                <br/>
                ISBN: $isbn
            </td>
            <td>$author</td>
            <td>$title</td>
            <td>$price</td>
            <td><form method="POST" action="?">
                <button class="btn btn-primary"><b>Add to Cart</b></button>
                <input type="hidden" name="username" value="$username">
                <input type="hidden" name="purchase" value="$isbn">
            </form></td>
        </tr>

eof
    }

    my $htmlFooter = <<eof;
    </tbody>
    </table>
	<p>

eof

   return $htmlHeader . $resultTable . $htmlFooter;
}

sub basket_results {
    my @matching_isbns = read_basket($username);

	my $htmlHeader = <<eof;
    <div style="margin-left: 10%">
        <h2>Cart for $username:</h2>
    </div>
    <table class="table table-hover" style="margin-left: 10%; width:70%">
    <thead>
        <tr>
            <th>Book</th>
            <th>Authors</th>
            <th>Title</th>
            <th>Price</th>
            <th>
        </tr>
    </thead>
    <tbody>

eof

    my $resultTable = "";
    foreach my $isbn (@matching_isbns) {
        my $price = $book_details{$isbn}{price};
        my $title = $book_details{$isbn}{title};
        my $author = $book_details{$isbn}{authors};
        my $imageURL = $book_details{$isbn}{mediumimageurl};
        my $imageHeight = $book_details{$isbn}{mediumimageheight};
        my $imageWidth = $book_details{$isbn}{mediumimagewidth};
        $resultTable .= <<eof;
        <tr>
            <td>
                <image src=$imageURL width=$imageWidth height=$imageHeight>
                <br/>
                ISBN: $isbn
            </td>
            <td>$author</td>
            <td>$title</td>
            <td>$price</td>
        </tr>

eof
    }

    my $htmlFooter = <<eof;
    </tbody>
    </table>
	<p>

eof

   return $htmlHeader . $resultTable . $htmlFooter;
}

#
# HTML at top of every screen
#
sub page_header() {
	my $header = <<eof;
Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
<head>
<title>Mekong: All the books you could want!</title>
<link href="//netdna.bootstrapcdn.com/bootstrap/3.0.1/css/bootstrap.min.css" rel="stylesheet">
<script src="//netdna.bootstrapcdn.com/bootstrap/3.0.1/js/bootstrap.min.js"></script>
<style> 
    body {
        padding-top: 50px;
    }
</style>
</head>
<body>

eof
    return $header;
}

sub navbar() {
    our $username = $_[0];
    my $navbar = <<eof;
<nav class="navbar navbar-default navbar-fixed-top" role="navigation">
    <div class="navbar-header" style="margin-left: 10%">
        <a class="navbar-brand" href="mekong.cgi">Mekong</a>
    </div>


    <form class="navbar-form navbar-left" role="search" style="width:20%">
        <div class="input-group">
            <input type="text" class="form-control" name="search_terms" placeholder="Search">
            <div class="input-group-btn">
                <button class="btn btn-default" type="submit"><i class="glyphicon glyphicon-search"></i></button>
                <input type="hidden" value=$username name="username">
            </div>
        </div>
    </form>

    <ul class="nav navbar-nav navbar-right" style="margin-right: 20%">
        <li><a href="?view=orders&username=$username">View Orders</a></li>
        <li><a href="?view=cart&username=$username">View Cart</a></li>
        <li><a href="?logout=true">Logout</a></li>
    </ul>
</nav>

eof
    return $navbar;
}

#
# HTML at bottom of every screen
#
sub page_trailer() {
	my $debugging_info = debugging_info();
	
	return <<eof;
	$debugging_info
<body>
</html>

eof

}

#
# Print out information for debugging purposes
#
sub debugging_info() {
	my $params = "";
	foreach $p (param()) {
		$params .= "param($p)=".param($p)."\n"
	}

    for my $key (keys(%{$book_details{"0394507606"}})) {
        $params .= ("keys are $key = $book_details{'0394507606'}{$key}\n");
    }

	return <<eof;
<hr>
<h4>Debugging information - parameter values supplied to $0</h4>
<pre>
$params
</pre>
<hr>

eof

}




###
### Below here are utility functions
### Most are unused by the code above, but you will 
### need to use these functions (or write your own equivalent functions)
### 
###

# return true if specified string can be used as a login

sub legal_username {
	my ($username) = @_;
	our ($last_error);

	if ($username !~ /^[a-zA-Z][a-zA-Z0-9]*$/) {
		$last_error = "Invalid login '$username': logins must start with a letter and contain only letters and digits.";
		return 0;
	}
	if (length $username < 3 || length $username > 8) {
		$last_error = "Invalid login: logins must be 3-8 characters long.";
		return 0;
	}
	return 1;
}

# return true if specified string can be used as a password

sub legal_password {
	my ($password) = @_;
	our ($last_error);
	
	if ($password =~ /\s/) {
		$last_error = "Invalid password: password can not contain white space.";
		return 0;
	}
	if (length $password < 5) {
		$last_error = "Invalid password: passwords must contain at least 5 characters.";
		return 0;
	}
	return 1;
}


# return true if specified string could be an ISBN

sub legal_isbn {
	my ($isbn) = @_;
	our ($last_error);
	
	return 1 if $isbn =~ /^\d{9}(\d|X)$/;
	$last_error = "Invalid isbn '$isbn' : an isbn must be exactly 10 digits.";
	return 0;
}


# return true if specified string could be an credit card number

sub legal_credit_card_number {
	my ($number) = @_;
	our ($last_error);
	
	return 1 if $number =~ /^\d{16}$/;
	$last_error = "Invalid credit card number - must be 16 digits.\n";
	return 0;
}

# return true if specified string could be an credit card expiry date

sub legal_expiry_date {
	my ($expiry_date) = @_;
	our ($last_error);
	
	return 1 if $expiry_date =~ /^\d\d\/\d\d$/;
	$last_error = "Invalid expiry date - must be mm/yy, e.g. 11/04.\n";
	return 0;
}



# return total cost of specified books

sub total_books {
	my @isbns = @_;
	our %book_details;
	$total = 0;
	foreach $isbn (@isbns) {
		die "Internal error: unknown isbn $isbn  in total_books" if !$book_details{$isbn}; # shouldn't happen
		my $price = $book_details{$isbn}{price};
		$price =~ s/[^0-9\.]//g;
		$total += $price;
	}
	return $total;
}

# return true if specified login & password are correct
# user's details are stored in hash user_details

sub authenticate {
	my ($username, $password) = @_;
	our (%user_details, $last_error);
	
	return 0 if !legal_username($username);
	if (!open($USER, "$users_dir/$username")) {
		$last_error = "User '$username' does not exist.";
		return 0;
	}
	my %details =();
	while (<$USER>) {
		next if !/^([^=]+)=(.*)/;
		$details{$1} = $2;
	}
	close(USER);
	foreach $field (qw(name street city state postcode password)) {
		if (!defined $details{$field}) {
 	 	 	$last_error = "Incomplete user file: field $field missing";
			return 0;
		}
	}
	if ($details{"password"} ne $password) {
  	 	$last_error = "Incorrect password.";
		return 0;
	 }
	 %user_details = %details;
  	 return 1;
}

sub new_account {
	my ($username, $password, $name, $street, $city, $state, $postcode, $email) = @_;
    my %details;
    $details{"username"} = $username;
    $details{"password"} = $password;
    $details{"name"} = $name;
    $details{"street"} = $street;
    $details{"city"} = $city;
    $details{"state"} = $state;
    $details{"postcode"} = $postcode;
    $details{"email"} = $email;
    our $last_error;
	if (!legal_username($username)) {
		return 0;
	}
    our ($users_dir);
	if (-r "$users_dir/$username") {
		$last_error = "Invalid user name: login already exists.\n";
		return 0;
	}

    my $details = "";
	foreach $description (@new_account_rows) {
		my ($name, $label)  = split /\|/, $description;
		next if $name eq "login";
		my $value = $details{$name};
        chomp $value;
        if ($name eq "password" && !legal_password($value)) {
            return 0;
        }
        if ($value =~ m/^\s*$/) {
            $last_error = "$name must not be empty.";
            return 0;
        }
		$user_details{$name} = $value;
		$details .= "$name=$value\n";
	}
	if (!open($USER, ">$users_dir/$username")) {
		$last_error = "Can not create user file $users_dir/$username: $!";
		return 0;
	}
    print $USER $details if defined $USER;
    if (!defined $USER) {
        print("Error when writing file: $!");
    }
	close $USER;
	return $username;
}

# read contents of files in the books dir into the hash book
# a list of field names in the order specified in the file
 
sub read_books {
	my ($books_file) = @_;
	our %book_details;
	print STDERR "read_books($books_file)\n" if $debug;
	open BOOKS, $books_file or die "Can not open books file '$books_file'\n";
	my $isbn;
	while (<BOOKS>) {
		if (/^\s*"(\d+X?)"\s*:\s*{\s*$/) {
			$isbn = $1;
			next;
		}
		next if !$isbn;
		my ($field, $value);
		if (($field, $value) = /^\s*"([^"]+)"\s*:\s*"(.*)",?\s*$/) {
			$attribute_names{$field}++;
			print STDERR "$isbn $field-> $value\n" if $debug > 1;
			$value =~ s/([^\\]|^)\\"/$1"/g;
	  		$book_details{$isbn}{$field} = $value;
		} elsif (($field) = /^\s*"([^"]+)"\s*:\s*\[\s*$/) {
			$attribute_names{$1}++;
			my @a = ();
			while (<BOOKS>) {
				last if /^\s*\]\s*,?\s*$/;
				push @a, $1 if /^\s*"(.*)"\s*,?\s*$/;
			}
	  		$value = join("\n", @a);
			$value =~ s/([^\\]|^)\\"/$1"/g;
	  		$book_details{$isbn}{$field} = $value;
	  		print STDERR "book{$isbn}{$field}=@a\n" if $debug > 1;
		}
	}
	close BOOKS;
}

# return books matching search string

sub search_books {
	my ($search_string) = @_;
	$search_string =~ s/\s*$//;
	$search_string =~ s/^\s*//;
	return search_books1(split /\s+/, $search_string);
}

# return books matching search terms

sub search_books1 {
	my (@search_terms) = @_;
	our %book_details;
	print STDERR "search_books1(@search_terms)\n" if $debug;
	my @unknown_fields = ();
	foreach $search_term (@search_terms) {
		push @unknown_fields, "'$1'" if $search_term =~ /([^:]+):/ && !$attribute_names{$1};
	}
	printf STDERR "$0: warning unknown field%s: @unknown_fields\n", (@unknown_fields > 1 ? 's' : '') if @unknown_fields;
	my @matches = ();
	BOOK: foreach $isbn (sort keys %book_details) {
		my $n_matches = 0;
		if (!$book_details{$isbn}{'=default_search='}) {
			$book_details{$isbn}{'=default_search='} = ($book_details{$isbn}{title} || '')."\n".($book_details{$isbn}{authors} || '');
			print STDERR "$isbn default_search -> '".$book_details{$isbn}{'=default_search='}."'\n" if $debug;
		}
		print STDERR "search_terms=@search_terms\n" if $debug > 1;
		foreach $search_term (@search_terms) {
			my $search_type = "=default_search=";
			my $term = $search_term;
			if ($search_term =~ /([^:]+):(.*)/) {
				$search_type = $1;
				$term = $2;
			}
			print STDERR "term=$term\n" if $debug > 1;
			while ($term =~ s/<([^">]*)"[^"]*"([^>]*)>/<$1 $2>/g) {}
			$term =~ s/<[^>]+>/ /g;
			next if $term !~ /\w/;
			$term =~ s/^\W+//g;
			$term =~ s/\W+$//g;
			$term =~ s/[^\w\n]+/\\b +\\b/g;
			$term =~ s/^/\\b/g;
			$term =~ s/$/\\b/g;
			next BOOK if !defined $book_details{$isbn}{$search_type};
			print STDERR "search_type=$search_type term=$term book=$book_details{$isbn}{$search_type}\n" if $debug;
			my $match;
			eval {
				my $field = $book_details{$isbn}{$search_type};
				# remove text that looks like HTML tags (not perfect)
				while ($field =~ s/<([^">]*)"[^"]*"([^>]*)>/<$1 $2>/g) {}
				$field =~ s/<[^>]+>/ /g;
				$field =~ s/[^\w\n]+/ /g;
				$match = $field !~ /$term/i;
			};
			if ($@) {
				$last_error = $@;
				$last_error =~ s/;.*//;
				return (); 
			}
			next BOOK if $match;
			$n_matches++;
		}
		push @matches, $isbn if $n_matches > 0;
	}
	
	sub bySalesRank {
		my $max_sales_rank = 100000000;
		my $s1 = $book_details{$a}{SalesRank} || $max_sales_rank;
		my $s2 = $book_details{$b}{SalesRank} || $max_sales_rank;
		return $a cmp $b if $s1 == $s2;
		return $s1 <=> $s2;
	}
	
	return sort bySalesRank @matches;
}


# return books in specified user's basket

sub read_basket {
	my ($username) = @_;
	our %book_details;
	open F, "$baskets_dir/$username" or return ();
	my @isbns = <F>;

	close(F);
	chomp(@isbns);
	!$book_details{$_} && die "Internal error: unknown isbn $_ in basket\n" foreach @isbns;
	return @isbns;
}


# delete specified book from specified user's basket
# only first occurance is deleted

sub delete_basket {
	my ($username, $delete_isbn) = @_;
	my @isbns = read_basket($username);
	open F, ">$baskets_dir/$username" or die "Can not open $baskets_dir/$username: $!";
	foreach $isbn (@isbns) {
		if ($isbn eq $delete_isbn) {
			$delete_isbn = "";
			next;
		}
		print F "$isbn\n";
	}
	close(F);
	unlink "$baskets_dir/$username" if ! -s "$baskets_dir/$username";
}


# add specified book to specified user's basket

sub add_basket {
	my ($username, $isbn) = @_;
	open F, ">>$baskets_dir/$username" or die "Can not open $baskets_dir/$username::$! \n";
	print F "$isbn\n";
	close(F);
}


# finalize specified order

sub finalize_order {
	my ($username, $credit_card_number, $expiry_date) = @_;
	my $order_number = 0;

	if (open ORDER_NUMBER, "$orders_dir/NEXT_ORDER_NUMBER") {
		$order_number = <ORDER_NUMBER>;
		chomp $order_number;
		close(ORDER_NUMBER);
	}
	$order_number++ while -r "$orders_dir/$order_number";
	open F, ">$orders_dir/NEXT_ORDER_NUMBER" or die "Can not open $orders_dir/NEXT_ORDER_NUMBER: $!\n";
	print F ($order_number + 1);
	close(F);

	my @basket_isbns = read_basket($username);
	open ORDER,">$orders_dir/$order_number" or die "Can not open $orders_dir/$order_number:$! \n";
	print ORDER "order_time=".time()."\n";
	print ORDER "credit_card_number=$credit_card_number\n";
	print ORDER "expiry_date=$expiry_date\n";
	print ORDER join("\n",@basket_isbns)."\n";
	close(ORDER);
	unlink "$baskets_dir/$username";
	
	open F, ">>$orders_dir/$username" or die "Can not open $orders_dir/$username:$! \n";
	print F "$order_number\n";
	close(F);
	
}


# return order numbers for specified login

sub login_to_orders {
	my ($username) = @_;
	open F, "$orders_dir/$username" or return ();
	@order_numbers = <F>;
	close(F);
	chomp(@order_numbers);
	return @order_numbers;
}



# return contents of specified order

sub read_order {
	my ($order_number) = @_;
	open F, "$orders_dir/$order_number" or warn "Can not open $orders_dir/$order_number:$! \n";
	@lines = <F>;
	close(F);
	chomp @lines;
	foreach (@lines[0..2]) {s/.*=//};
	return @lines;
}

###
### functions below are only for testing from the command line
### Your do not need to use these funtions
###

sub console_main {
	set_global_variables();
	$debug = 1;
	foreach $dir ($orders_dir,$baskets_dir,$users_dir) {
		if (! -d $dir) {
			print "Creating $dir\n";
			mkdir($dir, 0777) or die("Can not create $dir: $!");
		}
	}
	read_books($books_file);
	my @commands = qw(login new_account search details add drop basket checkout orders quit);
	my @commands_without_arguments = qw(basket checkout orders quit);
	my $username = "";
	
	print "mekong.com.au - ASCII interface\n";
	while (1) {
		$last_error = "";
		print "> ";
		$line = <STDIN> || last;
		$line =~ s/^\s*>\s*//;
		$line =~ /^\s*(\S+)\s*(.*)/ || next;
		($command, $argument) = ($1, $2);
		$command =~ tr/A-Z/a-z/;
		$argument = "" if !defined $argument;
		$argument =~ s/\s*$//;
		
		if (
			$command !~ /^[a-z_]+$/ ||
			!grep(/^$command$/, @commands) ||
			grep(/^$command$/, @commands_without_arguments) != ($argument eq "") ||
			($argument =~ /\s/ && $command ne "search")
		) {
			chomp $line;
			$line =~ s/\s*$//;
			$line =~ s/^\s*//;
			incorrect_command_message("$line");
			next;
		}

		if ($command eq "quit") {
			print "Thanks for shopping at mekong.com.au.\n";
			last;
		}
		if ($command eq "login") {
			$username = login_command($argument);
			next;
		} elsif ($command eq "new_account") {
			$username = new_account_command($argument);
			next;
		} elsif ($command eq "search") {
			search_command($argument);
			next;
		} elsif ($command eq "details") {
			details_command($argument);
			next;
		}
		
		if (!$username) {
			print "Not logged in.\n";
			next;
		}
		
		if ($command eq "basket") {
			basket_command($username);
		} elsif ($command eq "add") {
			add_command($username, $argument);
		} elsif ($command eq "drop") {
			drop_command($username, $argument);
		} elsif ($command eq "checkout") {
			checkout_command($username);
		} elsif ($command eq "orders") {
			orders_command($username);
		} else {
			warn "internal error: unexpected command $command";
		}
	}
}

sub login_command {
	my ($username) = @_;
	if (!legal_username($username)) {
		print "$last_error\n";
		return "";
	}
	if (!-r "$users_dir/$username") {
		print "User '$username' does not exist.\n";
		return "";
	}
	printf "Enter password: ";
	my $pass = <STDIN>;
	chomp $pass;
	if (!authenticate($username, $pass)) {
		print "$last_error\n";
		return "";
	}
	$username = $username;
	print "Welcome to mekong.com.au, $username.\n";
	return $username;
}

sub new_account_command {
	my ($username) = @_;
	if (!legal_username($username)) {
		print "$last_error\n";
		return "";
	}
	if (-r "$users_dir/$username") {
		print "Invalid user name: login already exists.\n";
		return "";
	}
	if (!open(USER, ">$users_dir/$username")) {
		print "Can not create user file $users_dir/$username: $!";
		return "";
	}
	foreach $description (@new_account_rows) {
		my ($name, $label)  = split /\|/, $description;
		next if $name eq "login";
		my $value;
		while (1) {
			print "$label ";
			$value = <STDIN>;
			exit 1 if !$value;
			chomp $value;
			if ($name eq "password" && !legal_password($value)) {
				print "$last_error\n";
				next;
			}
			last if $value =~ /\S+/;
		}
		$user_details{$name} = $value;
		print USER "$name=$value\n";
	}
	close(USER);
	print "Welcome to mekong.com.au, $username.\n";
	return $username;
}

sub search_command {
	my ($search_string) = @_;
	$search_string =~ s/\s*$//;
	$search_string =~ s/^\s*//;
	search_command1(split /\s+/, $search_string);
}

sub search_command1 {
	my (@search_terms) = @_;
	my @matching_isbns = search_books1(@search_terms);
	if ($last_error) {
		print "$last_error\n";
	} elsif (@matching_isbns) {
		print_books(@matching_isbns);
	} else {
		print "No books matched.\n";
	}
}

sub details_command {
	my ($isbn) = @_;
	our %book_details;
	if (!legal_isbn($isbn)) {
		print "$last_error\n";
		return;
	}
	if (!$book_details{$isbn}) {
		print "Unknown isbn: $isbn.\n";
		return;
	}
	print_books($isbn);
	foreach $attribute (sort keys %{$book_details{$isbn}}) {
		next if $attribute =~ /Image|=|^(|price|title|authors|productdescription)$/;
		print "$attribute: $book_details{$isbn}{$attribute}\n";
	}
	my $description = $book_details{$isbn}{productdescription} or return;
	$description =~ s/\s+/ /g;
	$description =~ s/\s*<p>\s*/\n\n/ig;
	while ($description =~ s/<([^">]*)"[^"]*"([^>]*)>/<$1 $2>/g) {}
	$description =~ s/(\s*)<[^>]+>(\s*)/$1 $2/g;
	$description =~ s/^\s*//g;
	$description =~ s/\s*$//g;
	print "$description\n";
}

sub basket_command {
	my ($username) = @_;
	my @basket_isbns = read_basket($username);
	if (!@basket_isbns) {
		print "Your shopping basket is empty.\n";
	} else {
		print_books(@basket_isbns);
		printf "Total: %11s\n", sprintf("\$%.2f", total_books(@basket_isbns));
	}
}

sub add_command {
	my ($username,$isbn) = @_;
	our %book_details;
	if (!legal_isbn($isbn)) {
		print "$last_error\n";
		return;
	}
	if (!$book_details{$isbn}) {
		print "Unknown isbn: $isbn.\n";
		return;
	}
	add_basket($username, $isbn);
}

sub drop_command {
	my ($username,$isbn) = @_;
	my @basket_isbns = read_basket($username);
	if (!legal_isbn($argument)) {
		print "$last_error\n";
		return;
	}
	if (!grep(/^$isbn$/, @basket_isbns)) {
		print "Isbn $isbn not in shopping basket.\n";
		return;
	}
	delete_basket($username, $isbn);
}

sub checkout_command {
	my ($username) = @_;
	my @basket_isbns = read_basket($username);
	if (!@basket_isbns) {
		print "Your shopping basket is empty.\n";
		return;
	}
	print "Shipping Details:\n$user_details{name}\n$user_details{street}\n$user_details{city}\n$user_details{state}, $user_details{postcode}\n\n";
	print_books(@basket_isbns);
	printf "Total: %11s\n", sprintf("\$%.2f", total_books(@basket_isbns));
	print "\n";
	my ($credit_card_number, $expiry_date);
	while (1) {
			print "Credit Card Number: ";
			$credit_card_number = <>;
			exit 1 if !$credit_card_number;
			$credit_card_number =~ s/\s//g;
			next if !$credit_card_number;
			last if $credit_card_number =~ /^\d{16}$/;
			last if legal_credit_card_number($credit_card_number);
			print "$last_error\n";
	}
	while (1) {
			print "Expiry date (mm/yy): ";
			$expiry_date = <>;
			exit 1 if !$expiry_date;
			$expiry_date =~ s/\s//g;
			next if !$expiry_date;
			last if legal_expiry_date($expiry_date);
			print "$last_error\n";
	}
	finalize_order($username, $credit_card_number, $expiry_date);
}

sub orders_command {
	my ($username) = @_;
	print "\n";
	foreach $order (login_to_orders($username)) {
		my ($order_time, $credit_card_number, $expiry_date, @isbns) = read_order($order);
		$order_time = localtime($order_time);
		print "Order #$order - $order_time\n";
		print "Credit Card Number: $credit_card_number (Expiry $expiry_date)\n";
		print_books(@isbns);
		print "\n";
	}
}

# print descriptions of specified books
sub print_books(@) {
	my @isbns = @_;
	print get_book_descriptions(@isbns);
}

# return descriptions of specified books
sub get_book_descriptions {
	my @isbns = @_;
	my $descriptions = "";
	our %book_details;
	foreach $isbn (@isbns) {
		die "Internal error: unknown isbn $isbn in print_books\n" if !$book_details{$isbn}; # shouldn't happen
		my $title = $book_details{$isbn}{title} || "";
		my $authors = $book_details{$isbn}{authors} || "";
		$authors =~ s/\n([^\n]*)$/ & $1/g;
		$authors =~ s/\n/, /g;
		$descriptions .= sprintf "%s %7s %s - %s\n", $isbn, $book_details{$isbn}{price}, $title, $authors;
	}
	return $descriptions;
}

sub set_global_variables {
	$base_dir = ".";
	$books_file = "$base_dir/books.json";
	$orders_dir = "$base_dir/orders";
	$baskets_dir = "$base_dir/baskets";
	$users_dir = "$base_dir/users";
	$last_error = "";
	%user_details = ();
	%book_details = ();
	%attribute_names = ();
	@new_account_rows = (
		  'login|Login:|10',
		  'password|Password:|10',
		  'name|Full Name:|50',
		  'street|Street:|50',
		  'city|City/Suburb:|25',
		  'state|State:|25',
		  'postcode|Postcode:|25',
		  'email|Email Address:|35'
		  );
}


sub incorrect_command_message {
	my ($command) = @_;
	print "Incorrect command: $command.\n";
	print <<eof;
Possible commands are:
login <login-name>
new_account <login-name>                    
search <words>
details <isbn>
add <isbn>
drop <isbn>
basket
checkout
orders
quit
eof
}


