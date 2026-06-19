import httpx
import pytest

from dict_crawler.http import create_client


@pytest.fixture
def client():
    client = create_client()
    yield client
    # client.close() — httpx AsyncClient requires await


@pytest.fixture
def sample_html():
    return """
    <html><body>
      <div class="pr di superentry">
        <div class="c_hh">English <span>|</span> American Dictionary</div>
        <div class="entry-body__el">
          <span class="headword">hello</span>
          <span class="pos dpos">exclamation</span>
          <div class="pr.dsense">
            <div class="epp-xref.dxref">A1</div>
            <div class="def-block ddef_block">
              <div class="def ddef_d db">used as a greeting</div>
              <div class="examp dexamp">
                <div class="eg deg">Hello, how are you?</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </body></html>
    """


@pytest.fixture
def word_not_found_html():
    return """
    <html><body>
      <div class="result-body">
        <div class="h" style="display:block;">No result found for <b>xyznotaword</b></div>
      </div>
    </body></html>
    """
