import { Component, OnInit, Inject } from '@angular/core';
import { Problem } from '../../models/problem.model';
import { Subscription } from 'rxjs/internal/Subscription';

@Component({
  selector: 'app-problem-list',
  templateUrl: './problem-list.component.html',
  styleUrls: ['./problem-list.component.css']
})
export class ProblemListComponent implements OnInit {

  problems: Problem[] = [];
  subscriptionProblems: Subscription;
  searchTerm: string = '';
  subscriptionInput: Subscription;

  constructor(@Inject('data') private data,
              @Inject('input') private input) { }

  ngOnInit() {
    this.getProblems();
    this.getSearchTerm();
  }

  getProblems(): void {
    this.subscriptionProblems = this.data.getProblems()
                                          .subscribe(problems => this.problems = problems);
  }

  getSearchTerm(): void {
    this.subscriptionInput = this.input.getInput()
                                        .subscribe(term => this.searchTerm = term);
  }

}
