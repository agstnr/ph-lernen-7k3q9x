const {test} = require('node:test');
const assert = require('node:assert/strict');
const {correct, multiple} = require('../app/choice.js');
test('single choice requires exactly the correct option', () => {
 const q={optionen:[{richtig:false},{richtig:true},{richtig:false}]};
 assert.equal(multiple(q),false);
 assert.equal(correct(q,new Set([1])),true);
 for(const s of [[],[0],[1,2],[0,1,2]]) assert.equal(correct(q,new Set(s)),false);
});
test('multiple choice rejects partial answers and extra wrong options', () => {
 const q={optionen:[{richtig:true},{richtig:false},{richtig:true}]};
 assert.equal(multiple(q),true);
 assert.equal(correct(q,new Set([0,2])),true);
 for(const s of [[],[0],[2],[0,1,2]]) assert.equal(correct(q,new Set(s)),false);
});
