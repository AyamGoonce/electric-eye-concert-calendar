(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.a0b9131a742c022d.js","sha256":"a0b9131a742c022d11b1a8a053954dc523ff53f1bd701c2476359b00551cf914","count":2220,"publishedAt":"2026-10-06T18:40:31Z","state":"calendar-state.json","stateSha256":"da366ab28805a742c1e8049787aac0a3fb9ec213b4f1b7496e6d39ab61e15043","sourceState":"calendar-source-state.json","sourceStateSha256":"95929945474c858d1bec4f1c01a31a469254d0e168ea496e8521eba1380fcdfa"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
