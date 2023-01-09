from pyspark import keyword_only
from pyspark.ml import Transformer
from pyspark.ml.param.shared import HasInputCol, HasOutputCol, Param, Params, TypeConverters
from pyspark.ml.util import DefaultParamsReadable, DefaultParamsWritable
from pyspark.sql import DataFrame
from pyspark.sql.types import StringType, IntegerType
import pyspark.sql.functions as F

class AgeTransformer(Transformer, HasInputCol, HasOutputCol, DefaultParamsReadable, DefaultParamsWritable):
    input_col = Param(Params._dummy(), "input_col", "input column name.", typeConverter=TypeConverters.toString)
    output_col = Param(Params._dummy(), "output_col", "output column name.", typeConverter=TypeConverters.toString)
  
    @keyword_only
    def __init__(self, input_col: str = "input", output_col: str = "output"):
        super(AgeTransformer, self).__init__()
        self._setDefault(input_col=None, output_col=None)
        kwargs = self._input_kwargs
        self.set_params(**kwargs)
    
    @keyword_only
    def set_params(self, input_col: str = "input", output_col: str = "output"):
        kwargs = self._input_kwargs
        self._set(**kwargs)
    
    def get_input_col(self):
        return self.getOrDefault(self.input_col)
  
    def get_output_col(self):
        return self.getOrDefault(self.output_col)
  
    def _transform(self, df: DataFrame):
        decodeAgeMap = {'55-59':'57', '80 or older':'80', '65-69':'67', '75-79':'77','40-44':'42','70-74':'72','60-64':'62', '50-54':'52','45-49':'47','18-24':'21','35-39':'37', '30-34':'32','25-29':'27'}
        input_col = self.get_input_col()
        output_col = self.get_output_col()
        df = df.replace(decodeAgeMap, subset=[input_col])
        return df.withColumn(output_col, F.col(input_col).astype(IntegerType()))